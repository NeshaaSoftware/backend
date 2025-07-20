# from xml.etree import ElementTree as ET

# import requests
# from django.conf import settings


# def get_payammatni_credit():
#     soap_envelope = f"""<?xml version="1.0" encoding="utf-8"?>
# <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
#   <soap:Body>
#     <GetCredit xmlns="http://tempuri.org/">
#       <Username>{settings.ELANAK_USERNAME}</Username>
#       <Password>{settings.ELANAK_PASSWORD}</Password>
#     </GetCredit>
#   </soap:Body>
# </soap:Envelope>"""

#     # SOAP headers
#     headers = {"Content-Type": "text/xml; charset=utf-8", "SOAPAction": "http://tempuri.org/GetCredit"}

#     try:
#         # Make the SOAP request
#         response = requests.post(url="https://payammatni.com/webservice/send.php", data=soap_envelope, headers=headers, timeout=30)

#         # Check if request was successful
#         response.raise_for_status()

#         # Parse the SOAP response
#         root = ET.fromstring(response.content)

#         # Define namespaces based on the actual response
#         namespaces = {"SOAP-ENV": "http://schemas.xmlsoap.org/soap/envelope/", "ns1": "http://tempuri.org/"}

#         # Extract the result from the response
#         credit_result = root.find(".//ns1:GetCreditResponse/return", namespaces)
#         if credit_result is None:
#             # Try without namespace
#             credit_result = root.find(".//return")
#         if credit_result is None:
#             # Try with SOAP-ENV namespace
#             credit_result = root.find(".//SOAP-ENV:Body//return", namespaces)

#         if credit_result is not None:
#             return {"success": True, "credit": credit_result.text, "raw_response": response.text}
#         else:
#             # Check for SOAP fault
#             fault = root.find(".//soap:Fault", namespaces)
#             if fault is not None:
#                 fault_string = fault.find("faultstring")
#                 fault_code = fault.find("faultcode")
#                 return {
#                     "success": False,
#                     "error": "SOAP Fault",
#                     "fault_code": fault_code.text if fault_code is not None else "Unknown",
#                     "fault_string": fault_string.text if fault_string is not None else "Unknown error",
#                     "raw_response": response.text,
#                 }

#             return {"success": False, "error": "Unexpected response format", "raw_response": response.text}

#     except requests.exceptions.RequestException as e:
#         return {"success": False, "error": "Request failed", "details": str(e)}
#     except ET.ParseError as e:
#         return {
#             "success": False,
#             "error": "XML parsing failed",
#             "details": str(e),
#             "raw_response": getattr(locals().get("response"), "text", None),
#         }
#     except Exception as e:
#         return {"success": False, "error": "Unexpected error", "details": str(e)}
