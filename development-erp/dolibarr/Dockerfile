# Use an official PHP 8.1 + Apache image
FROM php:8.1-apache

# Install required dependencies and enable mysqli
RUN apt-get update && apt-get install -y \
    libmariadb-dev \
    && docker-php-ext-install mysqli \
    && docker-php-ext-enable mysqli

# Enable Apache modules if needed
RUN a2enmod rewrite

# Set the working directory and copy Dolibarr files
WORKDIR /var/www/html
COPY htdocs /var/www/html

# Set permissions
RUN chown -R www-data:www-data /var/www/html && chmod -R 755 /var/www/html

# Expose port 80
EXPOSE 80

CMD ["apache2-foreground"]
