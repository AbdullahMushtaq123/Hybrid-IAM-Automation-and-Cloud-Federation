import winrm

# 1. Connection Details to your Active Directory VM
# VM's IP address and Administrator password
VM_IP = "192.168.18.149" 
USERNAME = r"Administrator@local.Administrator.com"
PASSWORD = r"Password@123"

# 2. Mock HR New Hire Database
new_hires = [
    {"first": "Alice", "last": "Smith", "dept": "IT_Department", "title": "Cloud Engineer"},
    {"first": "Bob", "last": "Jones", "dept": "HR_Department", "title": "HR Specialist"},
    {"first": "Charlie", "last": "Miller", "dept": "IT_Department", "title": "Security Analyst"}
]

def provision_user(session, user):
    first_name = user["first"]
    last_name = user["last"]
    dept = user["dept"]
    title = user["title"]
    
    # Construct standard enterprise usernames: e.g., jsmith
    sam_account_name = f"{first_name[0].lower()}{last_name.lower()}"
    user_principal_name = f"{sam_account_name}@local.Administrator.com"
    display_name = f"{first_name} {last_name}"
    
    print(f"Creating account for {display_name} in {dept}...")
    
    # Raw PowerShell script to execute inside the Windows Server VM
    # This creates the user, sets a default secure password, enables the account, and puts it in the correct OU
    ps_script = f"""
    $passwd = ConvertTo-SecureString "Welcome2026!" -AsPlainText -Force
    New-ADUser -Name "{display_name}" `
               -GivenName "{first_name}" `
               -Surname "{last_name}" `
               -SamAccountName "{sam_account_name}" `
               -UserPrincipalName "{user_principal_name}" `
               -Path "OU={dept},OU=Enterprise_Users,DC=local,DC=Administrator,DC=com" `
               -Title "{title}" `
               -AccountPassword $passwd `
               -Enabled $true `
               -ChangePasswordAtLogon $true
    """
    
    # Run the command over the WinRM bridge
    result = session.run_ps(ps_script)
    
    if result.status_code == 0:
        print(f"Successfully provisioned: {sam_account_name}")
    else:
        print(f"Error provisioning {sam_account_name}: {result.std_err.decode('utf-8')}")

def main():
    # Establish connection session
    session = winrm.Session(f"http://{VM_IP}:5985/wsman", auth=(USERNAME, PASSWORD), transport='ntlm')
    
    # Process the queue
    for user in new_hires:
        provision_user(session, user)

if __name__ == "__main__":
    main()