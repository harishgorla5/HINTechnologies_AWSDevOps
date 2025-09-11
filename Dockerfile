FROM nginx:alpine
#Set working directory to nginx html folder
WORKDIR /usr/share/nginx/html                   
#Download your files from Github directly into image
ADD https://raw.githubusercontent.com/harishgorla5/HINTechnologies_AWSDevOps/refs/heads/main/index.html index.html
ADD https://raw.githubusercontent.com/harishgorla5/HINTechnologies_AWSDevOps/refs/heads/main/style.css style.css
