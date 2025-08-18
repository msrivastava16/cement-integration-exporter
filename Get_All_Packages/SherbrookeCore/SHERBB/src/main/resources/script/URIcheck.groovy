import com.sap.gateway.ip.core.customdev.util.Message;
import java.util.HashMap;
import groovy.xml.*;
import groovy.time.TimeCategory
import java.text.SimpleDateFormat

def Message processData(Message message) {
    
     def headers = message.getHeaders()
    
      // Retrieve the isCountRequested property
    def isCountRequested = headers.get("isCount")
    def itemCount = headers.get("ItemCount")
    
    // Get the response body
    def body = message.getBody(String)

        
    if (isCountRequested.equals("true")) {
        // Set the response to the count
       //  message.setBody(itemCount.toString())
                 message.setBody(body)
    } else {
        // Return the actual data set
        message.setBody(body)
    }
    return message
}