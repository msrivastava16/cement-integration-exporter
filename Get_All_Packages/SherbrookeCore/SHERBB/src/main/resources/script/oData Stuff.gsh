/*
 This script defines methods for processing and logging messages within
 SAP Cloud Integration using the Message API.

 The integration developer needs to create the method processData.
 This method takes a Message object from the package:
   com.sap.gateway.ip.core.customdev.util

 Available methods in the Message object include:
    - getBody()
    - setBody(Object)
    - getHeaders()
    - setHeaders(Map)
    - setHeader(String, Object)
    - getProperties()
    - setProperties(Map)
    - setProperty(String, Object)
*/

import com.sap.gateway.ip.core.customdev.util.Message
import java.util.HashMap
import java.net.URLDecoder
import java.nio.charset.Charset
import org.apache.olingo.odata2.api.uri.UriInfo
import com.sap.gateway.ip.core.customdev.logging.*
import groovy.json.JsonSlurper
import java.net.URI

// Main processing logic for the incoming message
def Message processData(Message message) {
    // Extract message body as a String
    def body = message.getBody(java.lang.String)
    def props = message.getProperties()

    // Create a message logger instance
    def messageLog = messageLogFactory.getMessageLog(message)

    // Log the body of the incoming message if logging is available
    if (messageLog != null) {
        messageLog.addAttachmentAsString('Incoming Message - Body', String.valueOf(body), 'text')
    }

    // Extract and log the full HTTP URL used for the request
    def oDataURL = message.getHeaders().get("CamelHttpUrl")
    if (messageLog != null) {
        messageLog.addAttachmentAsString('oDataURL', String.valueOf(oDataURL), 'text')
        messageLog.addAttachmentAsString('CamelHttpURL', String.valueOf(oDataURL), 'text')
    }

    // Store the HTTP URL in the message properties for downstream use
    message.setProperty("isCountRequested", oDataURL)

    // Extract URI information from the headers
    def uriInfo = message.getHeaders().get("UriInfo")

    // Extract key predicates from URI and set each as a message property
    def keyPredicates = uriInfo.getKeyPredicates()
    keyPredicates.each { keyPredicate ->
        def propertyName = keyPredicate.getProperty().getName()
        def propertyValue = keyPredicate.getLiteral()
        message.setProperty(propertyName, propertyValue)
    }

    // Handle OData `$top` parameter if present
    if (uriInfo.getTop() != null) {
        message.setProperty('top', uriInfo.getTop().toString())
    }

    // Handle OData `$skip` parameter or default to "0"
    message.setProperty('skip', uriInfo.getSkip() != null ? uriInfo.getSkip().toString() : "0")

    // Set flag indicating whether `$count=true` is used
    message.setProperty('isCount', uriInfo.isCount() ? "true" : "false")

    // Extract HTTP query string (e.g., everything after '?') from headers
    def httpQuery = message.getHeader('CamelHttpQuery', String)
    message.setProperty("httpQuery", httpQuery)

    // Parse and flatten the query string into message properties
    if (httpQuery) {
        def queryParameters = URLDecoder.decode(httpQuery, Charset.defaultCharset().name())
            .replace("\$", "")                       // Remove dollar signs (e.g., $top → top)
            .tokenize('&')                           // Split into individual key=value strings
            .collectEntries { it.tokenize('=') }     // Convert to map entries
        message.setProperties(queryParameters)
    }

    // Handle `$orderby` if present
    if (uriInfo.getOrderBy() != null) {
        def orderBy = uriInfo.getOrderBy()
        def orderByStr = orderBy.getUriLiteral().toString()

        // Save and expose orderBy string
        message.setProperty("orderBy", orderByStr)
        message.setHeader("orderBy", orderByStr)
    }

    // Handle `$filter` clause if present
    if (uriInfo.getFilter() != null) {
        def filter = uriInfo.getFilter()
        message.setProperty('filter', filter)

        def str = filter.getUriLiteral().toString()
        message.setProperty('filterStr', str)

        // Detect and extract substring used in a `substringof()` filter expression
        if (str.contains("substringof")) {
            def substringMatcher = (str =~ /(?i)substringof\('([^']*)'/)
            if (substringMatcher.find()) {
                message.setProperty('TextFilter', substringMatcher.group(1))
            }
        }

        // Helper function to extract filter value from URI literal
        def extractFilterValue = { String input, String fieldName ->
            def value = null
            def substringMatcher = (input =~ /(?i)substringof\('([^']*)',\s*${fieldName}\)/)
            if (substringMatcher.find()) {
                value = substringMatcher.group(1)
            } else {
                def eqMatcher = (input =~ /(?i)${fieldName}\s+eq\s+'([^']*)'/)
                if (eqMatcher.find()) {
                    value = eqMatcher.group(1)
                }
            }

            if (value != null) {
                value = value.replaceAll("\\)", "") // Remove closing parenthesis if present
            }
            return value
        }

        // Extract and set known field values as properties and headers
        ["ObjectID", "ParentID", "ObjectType", "ObjectSubtype"].each { field ->
            def val = extractFilterValue(str, field)
            if (val) {
                message.setProperty(field, val)
                message.setHeader(field, val)
            }
        }

        // Extract Filter0X fields and set as properties
        (1..5).each { i ->
            def field = "Filter0${i}"
            def val = extractFilterValue(str, field)
            if (val) {
                message.setProperty(field, val)
            }
        }

        // Extract custom Attrib0X filter fields and set as properties and headers
        (1..5).each { i ->
            def field = "Attrib0${i}"
            def val = extractFilterValue(str, field)
            if (val) {
                message.setProperty(field, val)
                message.setHeader(field, val)
            }
        }

        // Log extracted values for specific filter fields
        ["ObjectType", "ObjectSubtype", "Filter01", "Filter02", "Filter03", "Filter04", "Filter05"].each { field ->
            def value = message.getProperty(field)
            if (messageLog != null) {
                messageLog.addAttachmentAsString(field, String.valueOf(value), 'text')
            }
        }
    }

    return message
}

// Simple utility method to log the message body
def Message log(Message message) {
    def body = message.getBody(java.lang.String)
    def messageLog = messageLogFactory.getMessageLog(message)
    if (messageLog != null) {
        messageLog.addAttachmentAsString('body', String.valueOf(body), 'text')
    }
    return message
}