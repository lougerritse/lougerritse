<#
.SYNOPSIS
  <Overview of script>
    This script is provided with no warranties written nor implied. Use at your own risk.
    Limit Teams creation based upon group membership.
    This script will be used as a one time execution to limit the creation of Teams Sites based upon Group Membership. To
    disable this configuration run the script with a blank value for $GroupName and true for $AllowGroupCreation value.
.INPUTS
  <Inputs if any, otherwise state None>
    None
 .OUTPUTS
  <Outputs if any, otherwise state None - example: Log file stored in C:\Windows\Temp\<name>.log>
    None
.NOTES
    To disable restriction of Teams creation based upon group membership use the blank $GroupName and True lines!
    Currently Teams creation limited using the groupname:
    #$GroupName = "M365_Group_Creators"
    #$AllowGroupCreation = "False"
    #This would be used to allow everyone to create Teams again.
    #$GroupName = ""
    #$AllowGroupCreation = "True"
    - - - - - - - - - - - - - - - - - - - - - - - - - - -
    .EXAMPLE 
./M365_Group_Creators_Mod.ps1
#>


$GroupName = "M365_Group_Creators"
$AllowGroupCreation = "False"
Connect-AzureAD
$settingsObjectID = (Get-AzureADDirectorySetting | Where-object -Property Displayname -Value "Group.Unified" -EQ).id
if(!$settingsObjectID)
{
      $template = Get-AzureADDirectorySettingTemplate | Where-object {$_.displayname -eq "group.unified"}
    $settingsCopy = $template.CreateDirectorySetting()
    New-AzureADDirectorySetting -DirectorySetting $settingsCopy
    $settingsObjectID = (Get-AzureADDirectorySetting | Where-object -Property Displayname -Value "Group.Unified" -EQ).id
}
$settingsCopy = Get-AzureADDirectorySetting -Id $settingsObjectID
$settingsCopy["EnableGroupCreation"] = $AllowGroupCreation
if($GroupName)
{
    $settingsCopy["GroupCreationAllowedGroupId"] = (Get-AzureADGroup -Filter "DisplayName eq '$GroupName'").objectId
}
 else {
$settingsCopy["GroupCreationAllowedGroupId"] = $GroupName
}
Set-AzureADDirectorySetting -Id $settingsObjectID -DirectorySetting $settingsCopy
(Get-AzureADDirectorySetting -Id $settingsObjectID).Values
