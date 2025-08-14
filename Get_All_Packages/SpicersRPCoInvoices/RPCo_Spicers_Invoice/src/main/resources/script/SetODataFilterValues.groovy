import com.sap.gateway.ip.core.customdev.util.Message;
import java.nio.charset.Charset
import java.text.SimpleDateFormat;
import java.util.Date;
import java.text.ParseException;

def Message processData(Message message) {
    // Default to customer 104184.
    String filter = "Customer eq '0000104184'";
    // Default to all invoices since 2023-06-01.
    String invoiceDateFilter = " and InvoiceDate gt datetime'2023-06-01T00:00:00'";
    
    // Get the URL parameters passed in.
    String httpQuery = message.getHeader('CamelHttpQuery', String);
    if (httpQuery) {
        Map<String, String> queryParameters = URLDecoder.decode(httpQuery, Charset.defaultCharset().name())
			 .replace("\$","")
                .tokenize('&')
                .collectEntries { it.tokenize('=') };
                
        // If an InvoiceDate parameter has been passed in, filter for that date.
        String invoiceDate = queryParameters.get("InvoiceDate");
        if (invoiceDate && invoiceDate != null && invoiceDate != "") {
            // Need to check that it is only a date. Can only be in format YYYY-MM-DD.
            SimpleDateFormat dateFormat = new SimpleDateFormat("yyyy-MM-dd");
            try {
                Date parsedDate = dateFormat.parse(invoiceDate);
                // It's a valid date string.
                invoiceDateFilter = " and InvoiceDate eq datetime'" + invoiceDate + "T00:00:00'";
            } catch (ParseException pe) {
                // Not a valid format date. Force the call to the OData service to fail.
                invoiceDateFilter = " and InvoiceDate eq datetime'INVALIDT00:00:00'";
            }
        }
    }
    
    filter += invoiceDateFilter;
    
    message.setProperty("Filter", filter);
    
    return message;
}