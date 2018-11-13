from boxsdk import DevelopmentClient

client = DevelopmentClient()

search_term = 'SEARCH QUERY'
type = 'CONTENT TYPE'	# file, folder, or web_link
limit = 10
offset = 0

# Set search config fields
content = client.search(search_term, result_type=type, limit=limit, offset=offset)

box_file = client.file(file_id='11111').get()
output_file = open(box_file.name, 'wb')
box_file.download_to(output_file)