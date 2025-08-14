import com.sap.gateway.ip.core.customdev.util.Message;
import java.util.*;
import groovy.xml.*;

/********************************************************************************
 * This method logs the runtime error in the log file. 
 * *****************************************************************************/
def Message errorLog(Message message){
    def messageLog = messageLogFactory.getMessageLog(message)
    def map = message.getProperties()
    def ex = map.get("CamelExceptionCaught")
    // def body = message.getBody(java.lang.String)
    // body = XmlUtil.serialize(body.toString())
    // String appUrl = System.getenv("HC_APPLICATION_URL")
    // String tnmShortName = appUrl.substring(8, appUrl.indexOf("-"))
    // message.setProperty("TenantName", tnmShortName)
    if (ex!=null) {
        messageLog.addAttachmentAsString("Exception message:", ex.getMessage(), "text/plain")
    }
    // messageLog.addAttachmentAsString('Error Response',body.toString(),'text')
    return message
}


/********************************************************************************
 * This method logs the runtime error in the log file and prepares 
 * error response to client. 
 * *****************************************************************************/
def Message errorLogCreateWarehouseOrders(Message message){
    def messageLog = messageLogFactory.getMessageLog(message)
    def props = message.getProperties()
    def ex = props.get("CamelExceptionCaught")
    // def body = message.getBody(java.lang.String)
    // body = XmlUtil.serialize(body.toString())
    // String appUrl = System.getenv("HC_APPLICATION_URL")
    // String tnmShortName = appUrl.substring(8, appUrl.indexOf("-"))
    // message.setProperty("TenantName", tnmShortName)
    def error_body  =  ex.getResponseBody()
    error_body = XmlUtil.serialize(error_body.toString())
    if (ex!=null) {
        messageLog.addAttachmentAsString("Exception message:", ex.getMessage(), "text/plain")
        def ex_parsed = new XmlSlurper().parseText(error_body)
        def ex_mess    = ex_parsed?.Body?.Fault?.detail?.StandardFaultMessage?.standard?.faultText.toString()
        def masterBuilder = new StreamingMarkupBuilder()
        throw new Exception(ex_mess);          
    }

    
    def outputXml  = masterBuilder.bind{
       'WarehouseOrders'(){
           'WarehouseOrder'(){
               'OrderRefNumber'(props.get('OrderRefNumber'))
               'WarehouseNumber'(props.get('WarehouseNumber'))
               'TaskType'(props.get('taskType'))
               'WorkGroup'(props.get('WorkGroup'))
               'MessageType'('E')
               'Message'(ex_mess)
                //  'Message'(ex.toString())        //Commented by SSM
        
           }
       }
    }
    
    message.setBody(outputXml.toString())
    
    messageLog.addAttachmentAsString('Error Response',XmlUtil.serialize(outputXml.toString()),'text')
    
    // Added by SSM - Additional Exception handling
    def map = message.getHeaders();
    map.put("Content-Type",   "text/xml");
    map.put("CamelHttpResponseCode",   500);
  
    message.setBody(outputXml);
    throw new Exception(ex_mess + message.getProperty('CamelExceptionCaught'))
    return message
}