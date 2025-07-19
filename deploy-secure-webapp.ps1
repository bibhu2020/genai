
<#
.SYNOPSIS
This script deploys a secure Azure Web App environment.

.DESCRIPTION
The script provisions an Azure Web App and a Storage Account. The Web App is integrated with a Virtual Network
and communicates with the Storage Account via a private endpoint. Public access to the Web App is restricted to
an Azure Front Door instance, which acts as the single entry point.

.NOTES
- Ensure you have the Azure PowerShell (Az) module installed (`Install-Module -Name Az -AllowClobber -Scope CurrentUser`).
- Before running, connect to your Azure account using `Connect-AzAccount` and select the desired subscription with `Set-AzContext -Subscription "YourSubscriptionName"`.
#>

#region Variables
#=====================================================================================================================
# ---- Please update these variables before running the script ----

# Resource Naming and Location
$baseName = "gemini-secure-app" # A unique base name for all resources
$location = "EastUS" # Azure region for the resources

# Resource Group
$resourceGroupName = "${baseName}-rg"

# Networking
$vnetName = "${baseName}-vnet"
$appSubnetName = "AppServiceSubnet"
$privateEndpointSubnetName = "PrivateEndpointSubnet"
$vnetAddressPrefix = "10.0.0.0/16"
$appSubnetPrefix = "10.0.1.0/24"
$privateEndpointSubnetPrefix = "10.0.2.0/24"

# Storage Account
$storageAccountName = "st${baseName}$((Get-Random -Minimum 1000 -Maximum 9999))" # Unique name for storage
$storageSku = "Standard_LRS"

# App Service
$appServicePlanName = "${baseName}-plan"
$webAppName = "${baseName}-webapp"
$appServicePlanSku = "P1V2" # Premium V2 SKU is required for private endpoints

# Azure Front Door
$frontDoorProfileName = "${baseName}-afd"
$frontDoorEndpointName = "${baseName}-endpoint" # This will be part of the public URL
#endregion

#region Main Script
#=====================================================================================================================

# --- 1. Create Resource Group ---
Write-Host "Creating resource group '$resourceGroupName' in '$location'..."
New-AzResourceGroup -Name $resourceGroupName -Location $location -ErrorAction Stop

# --- 2. Create Virtual Network and Subnets ---
Write-Host "Creating VNet '$vnetName' with subnets..."
$appSubnet = New-AzVirtualNetworkSubnetConfig -Name $appSubnetName -AddressPrefix $appSubnetPrefix
$peSubnet = New-AzVirtualNetworkSubnetConfig -Name $privateEndpointSubnetName -AddressPrefix $privateEndpointSubnetPrefix

# Disable private endpoint network policies on the PE subnet. This is required.
$peSubnet.PrivateEndpointNetworkPolicies = "Disabled"

$virtualNetwork = New-AzVirtualNetwork -Name $vnetName -ResourceGroupName $resourceGroupName -Location $location -AddressPrefix $vnetAddressPrefix -Subnet $appSubnet, $peSubnet -ErrorAction Stop

# --- 3. Create Storage Account ---
Write-Host "Creating storage account '$storageAccountName'..."
$storageAccount = New-AzStorageAccount -ResourceGroupName $resourceGroupName -Name $storageAccountName -Location $location -SkuName $storageSku -Kind StorageV2 -ErrorAction Stop

# --- 4. Create Private Endpoint for Storage ---
Write-Host "Creating private endpoint for the storage account..."
$privateLinkResource = Get-AzPrivateLinkResource -ResourceGroupName $resourceGroupName -ResourceName $storageAccount.StorageAccountName -ResourceType "Microsoft.Storage/storageAccounts"
$storageSubResource = $privateLinkResource.RequiredZoneNames[0].Split('.')[1] # Extracts 'blob', 'table', etc.

$privateEndpointConnection = New-AzPrivateLinkServiceConnection -Name "${storageAccountName}-pls-conn" -PrivateLinkServiceId $storageAccount.Id -GroupId $storageSubResource
$privateEndpoint = New-AzPrivateEndpoint -ResourceGroupName $resourceGroupName -Name "${storageAccountName}-pe" -Location $location -Subnet (Get-AzVirtualNetwork -Name $vnetName -ResourceGroupName $resourceGroupName).Subnets[1] -PrivateLinkServiceConnection $privateEndpointConnection -ErrorAction Stop

# --- 5. Create Private DNS Zone for Storage Resolution ---
Write-Host "Configuring private DNS zone for storage..."
$dnsZoneName = "privatelink.${storageSubResource}.core.windows.net"
$privateDnsZone = New-AzPrivateDnsZone -ResourceGroupName $resourceGroupName -Name $dnsZoneName -ErrorAction Stop
$dnsNetworkLink = New-AzPrivateDnsVirtualNetworkLink -ResourceGroupName $resourceGroupName -ZoneName $dnsZoneName -Name "${vnetName}-dns-link" -VirtualNetworkId $virtualNetwork.Id -ErrorAction Stop
$dnsZoneGroup = New-AzPrivateDnsZoneGroup -ResourceGroupName $resourceGroupName -PrivateEndpointName $privateEndpoint.Name -Name "default" -PrivateDnsZoneConfig (New-AzPrivateDnsZoneConfig -Name $dnsZoneName -PrivateDnsZoneId $privateDnsZone.ResourceId) -ErrorAction Stop

# --- 6. Create App Service Plan and Web App ---
Write-Host "Creating App Service Plan '$appServicePlanName' and Web App '$webAppName'..."
$appServicePlan = New-AzAppServicePlan -Name $appServicePlanName -ResourceGroupName $resourceGroupName -Location $location -Tier $appServicePlanSku -ErrorAction Stop
$webApp = New-AzWebApp -Name $webAppName -ResourceGroupName $resourceGroupName -Location $location -Plan $appServicePlan.Name -ErrorAction Stop

# --- 7. Configure VNet Integration for the Web App ---
Write-Host "Integrating Web App with VNet..."
# The property `virtualNetworkSubnetId` is the required way to configure integration
Set-AzWebApp -ResourceGroupName $resourceGroupName -Name $webAppName -VirtualNetworkSubnetId $virtualNetwork.Subnets[0].Id -ErrorAction Stop

# --- 8. Create Azure Front Door (Standard SKU) ---
Write-Host "Creating Azure Front Door profile. This may take a few minutes..."
$afdProfile = New-AzCdnProfile -ProfileName $frontDoorProfileName -ResourceGroupName $resourceGroupName -SkuName "Standard_AzureFrontDoor" -Location "Global" -ErrorAction Stop

Write-Host "Configuring Front Door endpoint, origin group, and route..."
$originGroup = New-AzAfdOriginGroup -OriginGroupName "WebAppOriginGroup" -ResourceGroupName $resourceGroupName -ProfileName $afdProfile.Name -ProbeRequestType "HEAD" -ProbeProtocol "Https" -ProbeIntervalInSeconds 120
$origin = New-AzAfdOrigin -OriginName $webAppName -GroupName $originGroup.Name -ProfileName $afdProfile.Name -ResourceGroupName $resourceGroupName -HostName $webApp.DefaultHostName -OriginHostHeader $webApp.DefaultHostName -Priority 1 -Weight 1000

$endpoint = New-AzAfdEndpoint -EndpointName $frontDoorEndpointName -ProfileName $afdProfile.Name -ResourceGroupName $resourceGroupName -Location "Global" -EnabledState "Enabled"
New-AzAfdRoute -RouteName "DefaultRoute" -EndpointName $endpoint.Name -ProfileName $afdProfile.Name -ResourceGroupName $resourceGroupName -OriginGroup $originGroup -ForwardingProtocol "MatchRequest" -LinkToDefaultDomain "Enabled" -HttpsRedirect "Enabled"

# --- 9. Secure Web App to only allow Front Door traffic ---
Write-Host "Securing Web App to allow traffic only from Front Door..."
$frontDoorServiceTag = "AzureFrontDoor.Backend"
$afdId = $afdProfile.FrontDoorId

# Add the rule to allow AFD traffic. The header check is crucial for security.
Add-AzWebAppAccessRestrictionRule -ResourceGroupName $resourceGroupName -WebAppName $webAppName -Name "Allow-FrontDoor-ID" -Priority 100 -Action Allow -ServiceTag $frontDoorServiceTag -HttpHeader @{"X-Azure-FDID" = $afdId} -ErrorAction Stop

# Remove the default 'Allow all' rule
Remove-AzWebAppAccessRestrictionRule -ResourceGroupName $resourceGroupName -WebAppName $webAppName -Name "Allow all" -Force -ErrorAction Stop

# --- 10. Final Output ---
Write-Host "`n"
Write-Host "----------------------------------------------------------------" -ForegroundColor Green
Write-Host "         Deployment Finished Successfully!                      " -ForegroundColor Green
Write-Host "----------------------------------------------------------------" -ForegroundColor Green
Write-Host "`n"
Write-Host "Resource Group:      $resourceGroupName"
Write-Host "Web App Name:          $webAppName"
Write-Host "Web App URL (direct):  https://$($webApp.DefaultHostName) (Access should be forbidden)"
Write-Host "Front Door URL:        https://$($endpoint.HostName) (Use this URL to access the application)"
Write-Host "`n"
#endregion
