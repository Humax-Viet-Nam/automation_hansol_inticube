# update file content by curl:
- ex: curl -X PUT --data-binary "@test.txt" -H "Content-Type: text/plain"  http://192.168.100.247:8080/file_content