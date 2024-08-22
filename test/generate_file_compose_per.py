# generate_docker_compose.py

num_services = 100
start_port = 10801
base_image = '192.168.100.29:5000/hansol/initicube:1.0.0'
dockerfile_path = './Dockerfile'

# Start building the docker-compose content
docker_compose_content = 'version: \'3.8\'\n\nservices:\n'

for i in range(num_services):
    port = start_port + i
    service_name = f'web_{i+1}'
    docker_compose_content += f'  {service_name}:\n'
    docker_compose_content += f'    image: {base_image}\n'
    docker_compose_content += f'    build:\n'
    docker_compose_content += f'      context: .\n'
    docker_compose_content += f'      dockerfile: {dockerfile_path}\n'
    docker_compose_content += f'    ports:\n'
    docker_compose_content += f'      - "{port}:8080"\n'
    docker_compose_content += f'    environment:\n'
    docker_compose_content += f'      - PORT=8080\n'
    docker_compose_content += f'    volumes:\n'
    docker_compose_content += f'      - .:/app\n'
    docker_compose_content += f'    restart: always\n\n'

# Write to docker-compose.yml
with open('../docker-compose-per.yml', 'w') as file:
    file.write(docker_compose_content)

print("docker-compose.yml file generated successfully.")
