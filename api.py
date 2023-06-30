import json
import jwt
import pandas as pd
import requests
from azure.identity import InteractiveBrowserCredential



class PBI_API:
    """Power BI REST APIs

    Attributes:
        self.access_token (str): The acces token for the APIs
        self.df_workspaces (dataframe): All accessible worksapces
        self.df_workspaces_admin (dataframe): All accessible worksapces for admin
        self.user (str): User email
        self.proxies (dict): Proxy configuration
        self.base_url (str): Base url for the APIs
    """

    def __init__(self, proxy_url=None):
        #Proxy:
        if proxy_url != None:
            self.proxies = {
                "http": proxy_url
                # ,"https": proxy_url
            }
        else:
            self.proxies = None
            
        self.user=''
        self.base_url = "https://api.powerbi.com/v1.0/myorg/"
        
    def authenticate(self):
        """Get the access token for the rest APIs

        Raises:
            Exception: Con error if unable to connect
        """
       
        try:
            api = "https://analysis.windows.net/powerbi/api/.default"
            auth = InteractiveBrowserCredential(authority="https://login.microsoftonline.com/")
            access_token = auth.get_token(api)
            self.access_token = access_token.token
        except:
            raise Exception("Connection error")
        
        self.user_info()
            
    def user_info(self):
        
        def decode_token(access_token):
            decoded_token = jwt.decode(access_token, options={"verify_signature": False})
            return decoded_token

        decoded_token = decode_token(self.access_token)
        self.user=decoded_token['upn']
        
    def workspaces(self):
        """Get all accessible workspaces

        Raises:
            Exception: Connection error
        """
        dedicated_groups = "groups"
        
        final_url = self.base_url + dedicated_groups
        header = {"Authorization": f"Bearer {self.access_token}"}

        response = requests.get(final_url, headers=header, proxies=self.proxies)

        # Response code (200 = Success; 401 = Unauthorized; 404 = Bad Request)
        if response.status_code != 200:
            try:
                # Attempt to decode JSON response
               
                error_message = response.json()
            except ValueError:
                # If response cannot be decoded as JSON,
                # fallback to just return the raw response text
                error_message = response.text
                
            raise Exception(f"HTTP {response.status_code}\nServer message:\n[{error_message}]")
        
        else:
        
            workspaces = json.loads(response.content)
            # Concatenates all of the results into a single dataframe
            self.df_workspaces = pd.concat([pd.json_normalize(x) for x in workspaces["value"]]).reset_index(drop=True)
                   
    def admin_workspaces(self,top: int):
        """_summary_

        Args:
            top (int): Number of wks to return

        Raises:
            Exception: API error
        """
        base_url = "https://api.powerbi.com/v1.0/myorg/"
        dedicated_groups = "groups"
        
        final_url = base_url + "admin/" + dedicated_groups + f"?$top={top}"
        header = {"Authorization": f"Bearer {self.access_token}"}

        # HTTP GET Request
        response = requests.get(final_url, headers=header, proxies=self.proxies)

        # Response code (200 = Success; 401 = Unauthorized; 404 = Bad Request)
        if response.status_code != 200:
            try:
                # Attempt to decode JSON response
               
                error_message = response.json()
            except ValueError:
                # If response cannot be decoded as JSON,
                # fallback to just return the raw response text
                error_message = response.text
                
            raise Exception(f"{response.status_code}")
        
        else:
            workspaces = json.loads(response.content)
            # Concatenates all of the results into a single dataframe
            self.df_workspaces_admin = pd.concat([pd.json_normalize(x) for x in workspaces["value"]]).reset_index(drop=True)

        return response
    
    
    def add_to_workspace(self, wk_id: str,role:str,user_email:str):
        """Add user to workspace as an Contributor.

        Args:
            wk_id (str): workspace ID.
            role (str): Role: Admin, Member, Contributor, Viewer
            user_email (str): User email.

        Raises:
            Exception: error in the request.
        """
        base_url = f"https://api.powerbi.com/v1.0/myorg/admin/groups/{wk_id}/users"
        header = {"Authorization": f"Bearer {self.access_token}"}
        dict_content = {"groupUserAccessRight": role, "identifier": user_email, "principalType": "User"}
        
        
        response = requests.post(base_url, json=dict_content, headers=header, proxies=self.proxies)

        if response.status_code != 200:
            try:
                # Attempt to decode JSON response
               
                error_message = response.json()
            except ValueError:
                # If response cannot be decoded as JSON,
                # fallback to just return the raw response text
                error_message = response.text
                
            raise Exception(f"HTTP {response.status_code}\nServer message:\n[{error_message}]")

    def remove_from_workspace(self, wk_id: str,user_email:str):
        """Remove user from workspace.

        Args:
            wk_id (str): workspace ID.
            user_email (str): User email.

        Raises:
            Exception: error in the request.
        """
        base_url = f"https://api.powerbi.com/v1.0/myorg/admin/groups/{wk_id}/users/{user_email}"
        header = {"Authorization": f"Bearer {self.access_token}"}
        
        response = requests.delete(base_url, headers=header, proxies=self.proxies)
        
        if response.status_code != 200:
            try:
                # Attempt to decode JSON response
               
                error_message = response.json()
            except ValueError:
                # If response cannot be decoded as JSON,
                # fallback to just return the raw response text
                error_message = response.text
                
            raise Exception(f"HTTP {response.status_code}\nServer message:\n[{error_message}]")

        



    
    
    
    
    