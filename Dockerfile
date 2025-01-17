FROM public.ecr.aws/lambda/python:3.10

# Install git
RUN yum install -y git

# Copy requirements file
COPY requirements.txt ${LAMBDA_TASK_ROOT}

# Install the specified packages
RUN pip install -r requirements.txt
EXPOSE 8501

# Handle Avachain installation
RUN pip uninstall -y avachain || true
RUN git clone -b cloud https://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@github.com/OnlinePage/Avachain.git /tmp/avachain && \
    cd /tmp/avachain && \
    pip install --no-cache-dir . && \
    rm -rf /tmp/avachain



# Set the working directory in the container
WORKDIR /app

# Copy the local code to the container image
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose Streamlit's default port
EXPOSE 8501

# Command to run the Streamlit app
CMD ["streamlit", "run", "frontUI.py", "--server.port=8501", "--server.enableCORS=false", "--server.enableXsrfProtection=false","app.handler","uvicorn", "lambda_function:app", "--host", "0.0.0.0", "--port", "8501"]



# Copy function code
COPY lambda_function.py ${LAMBDA_TASK_ROOT}/app.py

# Set the CMD to your handlerdxf

