# FinSolve RBAC Chatbot

### Overview

The FinSolve RBAC Chatbot is an intelligent, secure assistant developed for FinSolve Technologies. It empowers teams to quickly access the information they need, tailored to their specific roles. By integrating Retrieval-Augmented Generation (RAG) with Role-Based Access Control (RBAC), the chatbot delivers personalized and reliable responses sourced directly from department-specific documents, including financial reports, technical documentation, HR policies, and more.

### Key Features
**•	Role-Based Access Control:** Fine-grained document access, customized for each department.<br>
**•	Retrieval-Augmented Generation (RAG):** Combines vector search with large language models for context-rich answers.<br>
**•	Natural Language Interface:** Ask questions in plain English and receive clear responses.<br>
**•	Source-Aware Answers:** Every response includes source references for transparency.<br>
**•	Interactive Chat UI:** Real-time chat interface for seamless communication.<br>
**•	JWT Authentication:** Secure login and session management.<br>

### Role-Based Access Matrix 
<div align="center">
<img width="452" alt="image" src="https://github.com/user-attachments/assets/d42c393a-f2c0-46db-b6c8-858356a4a118" />
</div>

**Key:**
   •	✅ = Access granted (number indicates accessible files)<br>
   •	❌ = Access denied

This matrix shows how document access is restricted based on organizational roles, ensuring sensitive documents are only accessible to authorized teams. C-Level executives have full access, while other teams see only their department's documents and general docs.

**User access information (Sample Table):**
<div align="center">
<img width="452" alt="image" src="https://github.com/user-attachments/assets/6cb70501-3fb6-4493-83a3-ebf4e0f8ebb3" />
</div>

**Directory Description**
<div align="center">
<img width="452" alt="image" src="https://github.com/user-attachments/assets/f9fa8879-184f-402a-892c-8ea233e45767" />
</div>

**Project Structure**
<div align="center">
<img width="452" alt="image" src="https://github.com/user-attachments/assets/c929f760-e3a2-406f-8835-1722aefbfd91" />
</div>

**Project Architecture with tech stack**
<div align="center">
<img width="429" alt="image" src="https://github.com/user-attachments/assets/fb254df1-a797-4142-a1f5-c1d6e3a35809" />
</div>

### Installation
**1.Set Up Your Environment:** <br>
Clone the repository:<br>
   &nbsp;&nbsp; git clone https://github.com/yourusername/your-repo-name.git<br>
   &nbsp;&nbsp; cd your-repo-name<br>

**2.Create and activate a virtual environment:** <br>
   &nbsp;&nbsp;python -m venv venv<br>

#### On macOS/Linux:
source venv/bin/activate
#### On Windows:
venv\Scripts\activate


**3.Install dependencies:**
   &nbsp;&nbsp;Ensure requirements.txt exists in your root directory, then run:<br>
   &nbsp;&nbsp;pip install -r requirements.txt<br>
   
**4.Configure Environment Variables** <br>
   &nbsp;&nbsp;Create a .env file in your project root with sensitive info:<br>
   &nbsp;&nbsp;OPENAI_API_KEY=your_openai_api_key<br>
   &nbsp;&nbsp;SECRET_KEY=your_secret_key<br>
   
**5. Run the Application** <br>
   &nbsp;&nbsp;Start the FastAPI server with Uvicorn:<br>
   &nbsp;&nbsp;uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload<br>
   &nbsp;&nbsp;(Replace app.main:app with your actual FastAPI app path)<br>
   
**6. Access the Application** <br>
   &nbsp;&nbsp;Open your browser and navigate to:<br>
   &nbsp;&nbsp;**http://127.0.0.1:8000/** to view the main interface.<br>
     
### Security Highlights<br>
**•	JWT Authentication:** Secure login and session management.<br>
**•	Role-Based Filtering:** Results are filtered according to user roles.<br>
**•	Rate Limiting:** Prevents abuse and overload.<br>

### Future Enhancements<br>
**•	Multi-File Format Support:**  Extend input compatibility to include PDF, TXT, and DOC files. (Implementation already completed.)<br>
**•	LLM Switching:**  Enable seamless switching between various large language models (LLMs), including Claude 3 and LLaMA 3.<br>
**•	Advanced Security:**  Implement robust authentication using username and ID verification to enhance access control.<br>
**•	Admin Dashboard:**  Develop a centralized dashboard for managing user roles, document access, and system configurations.<br>
**•	CSV Export:**  Introduce CSV export functionality to allow structured data extraction for reporting and analysis.<br>
**•	LangChain + SQL Integration:**  Connect LangChain with a relational SQL database to enable advanced querying and structured response generation.<br>
**•	Secure Password Storage:**  Use PBKDF2-HMAC hashing to ensure secure and compliant password handling.<br>
**•	Sentiment Analysis:**  Incorporate sentiment analysis to understand user emotions and improve system responsiveness based on feedback.<br>
**•	Metadata-Based Chunk Ranking:**  Implement metadata grading to prioritize and organize retrieved content more effectively.<br>
**•	Model Quantization:**  Apply quantization techniques to optimize memory usage and improve system efficiency.<br>
**•	LoRA Fine-Tuning:**  Support Low-Rank Adaptation (LoRA) for efficient fine-tuning, enabling rapid customization and better performance with smaller datasets.<br>


### License & Acknowledgments <br>
This project is part of the Codebasics Resume Challenge and was developed for FinSolve Technologies.<br>
#### Acknowledgments:<br>
**•	Codebasics:** Project inspiration. 🙏<br>
  (https://codebasics.io/challenge/codebasics-gen-ai-data-science-resume-project-challenge)<br>
•	LangChain & Chroma: Vector search technology.<br>
•	DeepAI: LLM backbone.<br>
•	FastAPI: High-performance web API framework.<br>
•	Perplexity AI: Table and figure generation.<br>
•	All providers offering free-tier services.<br>

<br>
<br>
<br>
<br>
<br>


# DS RPC 01: Internal chatbot with role based access control

This is the starter repository for Codebasics's [Resume Project Challenge](https://codebasics.io/challenge/codebasics-gen-ai-data-science-resume-project-challenge) of building a RAG based Internal Chatbot with role based access control. Please fork this repository to get started.

Basic Authentication using FastAPI's `HTTPBasic` has been implemented in `main.py` for learners to get started with.

Visit the challenge page to learn more: [DS RPC-01](https://codebasics.io/challenge/codebasics-gen-ai-data-science-resume-project-challenge)
![alt text](resources/RPC_01_Thumbnail.jpg)
### Roles Provided
 - **engineering**
 - **finance**
 - **general**
 - **hr**
 - **marketing**
