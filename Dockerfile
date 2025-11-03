# Use an official lightweight Python image
FROM python:3.13-slim

# Set the working directory in the container
WORKDIR /app

# Install uv
RUN pip install uv

# Copy the dependency files
COPY pyproject.toml uv.lock* ./

# Install dependencies using uv
RUN uv pip install --no-cache --system .

# Apply patch to supabase-auth to fix with_config issue
RUN sed -i 's/@with_config(extra="allow")//g' /usr/local/lib/python3.13/site-packages/supabase_auth/types.py

# Copy the rest of the application code
COPY . .

# Command to run the application with gunicorn
CMD ["python","main.py"]
