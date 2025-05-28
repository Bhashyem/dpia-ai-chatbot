# Initialize the client
pega_client = PegaAPIClient(
    base_url="https://roche-gtech-dt1.pegacloud.net/prweb/api/v1/case",
    username="nadadhub",
    password="Pwrm*2025"
)

# Authenticate
if pega_client.authenticate():
    # Get case details
    case_details = pega_client.get_case("CASE-1234")
    if case_details:
        print("Case details:", case_details)
    
    # Create a new case
    new_case = pega_client.create_case(
        caseTypeID="Roche-Pathworks-Work-DPIA",
        processID="pyStartCase",
        content={}
    )
    
    # Update a case
    updated_case = pega_client.update_case(
        case_id="C-1234",  # Fixed: was 'cad', added missing comma
        content={
            "status": "In Progress",
            "assignedTo": "agent123"
        }
    )
    
    # Get case assignments
    assignments = pega_client.get_assignments("CASE-1234")
    if assignments:
        print("Case assignments:", assignments)
    
    # Close a case
    closed_case = pega_client.close_case(
        case_id="CASE-1234"
    )
    
    if closed_case:
        print("Case closed successfully:", closed_case)
else:
    print("Authentication failed") 