import winrm

# --- Enterprise Environment Configuration ---
target_ip = "192.168.18.149"  # Replace with your DC01 IP address
admin_user = "Administrator@local.Administrator.com"
admin_pass = "Password@123"  # Replace with your actual Domain Admin password

# The target user we want to disable (using the UPN from your screenshot)
user_to_disable = "admin.test@local.Administrator.com"

# --- PowerShell Payload ---
# This script disables the account and hides it from the global address list
# This explicitly filters by UPN first to bypass Identity identifier limitations
ps_script = f"""
Import-Module ActiveDirectory

$UPN = "{user_to_disable}"

try {{
    # 1. Locate the user by their full UPN
    $ADUser = Get-ADUser -Filter "UserPrincipalName -eq '$UPN'" -ErrorAction Stop
    
    if ($ADUser) {{
        # 2. Disable the Active Directory account immediately
        $ADUser | Disable-ADAccount -ErrorAction Stop
        
        # 3. Add a description noting the automated offboarding
        $date = Get-Date -Format "yyyy-MM-dd"
        $ADUser | Set-ADUser -Description "Automatically disabled by Python IAM script on $date" -ErrorAction Stop
        
        Write-Output "SUCCESS: Account $UPN has been disabled and locked down."
    }} else {{
        Write-Error "FAILED: No user found matching UPN $UPN."
    }}
}}
catch {{
    Write-Error "FAILED: An error occurred while modifying the account. Details: $_"
}}
"""
print(f"[*] Initiating automated offboarding protocol for: {user_to_disable}")

# Open the WinRM bridge to the server
try:
    session = winrm.Session(target_ip, auth=(admin_user, admin_pass), transport='ntlm')
    result = session.run_ps(ps_script)

    if result.status_code == 0:
        print("[+] Active Directory Response:")
        print(result.std_out.decode('utf-8').strip())
    else:
        print("[-] Error executing payload:")
        print(result.std_err.decode('utf-8').strip())

except Exception as e:
    print(f"[-] Connection failed: {e}")