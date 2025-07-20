import requests
from xml.etree import ElementTree as ET


def get_payammatni_credit(username, password):
    """
    Get credit information from PayamMatni web service using SOAP request.
    
    Args:
        username (str): PayamMatni username
        password (str): PayamMatni password
        
    Returns:
        dict: Response containing credit information or error details
    """
    
    # SOAP envelope for GetCredit method
    soap_envelope = f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
               xmlns:xsd="http://www.w3.org/2001/XMLSchema" 
               xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <GetCredit xmlns="http://tempuri.org/">
      <username>{username}</username>
      <password>{password}</password>
    </GetCredit>
  </soap:Body>
</soap:Envelope>"""
    
    # SOAP headers
    headers = {
        'Content-Type': 'text/xml; charset=utf-8',
        'SOAPAction': 'http://tempuri.org/GetCredit'
    }
    
    try:
        # Make the SOAP request
        response = requests.post(
            url='https://payammatni.com/webservice/send.php',
            data=soap_envelope,
            headers=headers,
            timeout=30
        )
        
        # Check if request was successful
        response.raise_for_status()
        
        # Parse the SOAP response
        root = ET.fromstring(response.content)
        
        # Define namespaces
        namespaces = {
            'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
            'tns': 'http://tempuri.org/'
        }
        
        # Extract the result from the response
        credit_result = root.find('.//tns:GetCreditResult', namespaces)
        
        if credit_result is not None:
            return {
                'success': True,
                'credit': credit_result.text,
                'raw_response': response.text
            }
        else:
            # Check for SOAP fault
            fault = root.find('.//soap:Fault', namespaces)
            if fault is not None:
                fault_string = fault.find('faultstring')
                fault_code = fault.find('faultcode')
                return {
                    'success': False,
                    'error': 'SOAP Fault',
                    'fault_code': fault_code.text if fault_code is not None else 'Unknown',
                    'fault_string': fault_string.text if fault_string is not None else 'Unknown error',
                    'raw_response': response.text
                }
            
            return {
                'success': False,
                'error': 'Unexpected response format',
                'raw_response': response.text
            }
            
    except requests.exceptions.RequestException as e:
        return {
            'success': False,
            'error': 'Request failed',
            'details': str(e)
        }
    except ET.ParseError as e:
        return {
            'success': False,
            'error': 'XML parsing failed',
            'details': str(e),
            'raw_response': getattr(locals().get('response'), 'text', None)
        }
    except Exception as e:
        return {
            'success': False,
            'error': 'Unexpected error',
            'details': str(e)
        }


def test_payammatni_connection(username, password):
    """
    Test the PayamMatni connection and return formatted result.
    
    Args:
        username (str): PayamMatni username
        password (str): PayamMatni password
        
    Returns:
        None: Prints the result to console
    """
    result = get_payammatni_credit(username, password)
    
    if result['success']:
        print(f"✅ Successfully connected to PayamMatni")
        print(f"📊 Credit: {result['credit']}")
    else:
        print(f"❌ Failed to connect to PayamMatni")
        print(f"🔍 Error: {result['error']}")
        if 'details' in result:
            print(f"📝 Details: {result['details']}")
        if 'fault_string' in result:
            print(f"🚨 SOAP Fault: {result['fault_string']}")
