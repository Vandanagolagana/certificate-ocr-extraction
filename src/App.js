import React, { useState } from "react";
import axios from "axios";
import Select from "react-select";
import "./App.css";
import HomeIcon from "@mui/icons-material/Home";

function App() {
    const [page, setPage] = useState(1);
    const [files, setFiles] = useState([]);
    const [uploadedFiles, setUploadedFiles] = useState([]);
    const [selectedAttributes, setSelectedAttributes] = useState([]);
    const [extractedData, setExtractedData] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [downloadLink, setDownloadLink] = useState("");
    const [certificateType, setCertificateType] = useState("");

    const idCardAttributes = [
        { value: "name", label: "Name" },
        { value: "dob", label: "Date of Birth" },
        { value: "roll no", label: "Roll No" },
        { value: "blood group", label: "Blood Group" },
        { value: "mobile", label: "Mobile" },
        { value: "emergency contact", label: "Emergency Contact" }
    ];

    const panCardAttributes = [
        { value: "name", label: "Name" },
        { value: "pan number", label: "PAN Number" },
        { value: "dob", label: "Date of Birth" },
        { value: "father's name", label: "Father's Name" }
    ];

    const aadharCardAttributes = [
      { value: "name", label: "Name" },
      { value: "dob", label: "Date of Birth" },
      { value: "gender", label: "Gender" },
      { value: "aadhar number", label: "Aadhar number" },
      { value: "address", label: "Address" }
    ];

    const tenthMarksheetAttributes = [
      { value: "name", label: "Name" },
      { value: "father name", label: "Father Name" },
      { value: "mother name", label: "Mother Name " },
      { value: "roll number", label: "Roll Number" },
      { value: "school name", label: "School Name" },
      { value: "dob", label: "Date Of Birth" },
      { value: "gpa", label: "Grade Points Average (GPA)" }// Example: You might want more specific marks fields
    ];

    const twelthMarksheetAttributes = [
        { value: "registered number", label: "Registered Number" },
        { value: "name", label: "Name" },
        { value: "father name", label: "Father Name" },
        { value: "mother name", label: "Mother Name" },
        { value: "aadhar number", label: "Aadhar Number" },
        //{ value: "grand total", label: "Grand Total" },
        // Example: More specific marks fields
    ];


    const handleFileChange = (event) => {
        setFiles([...files, ...Array.from(event.target.files)]);
    };

    const handleRefresh = () => {
      setPage(2); // Go back to certificate selection page
      setFiles([]);
      setUploadedFiles([]);
      setSelectedAttributes([]);
      setExtractedData([]);
      setLoading(false);
      setError("");
      setDownloadLink("");
      setCertificateType("");
  };
    const handleDeleteFile = (index) => {
        setFiles(files.filter((_, i) => i !== index));
    };

    const handleFileUpload = async () => {
        if (files.length === 0 || selectedAttributes.length === 0) {
            setError("Please select files and attributes.");
            return;
        }
        setError("");
        setLoading(true);

        const attributeArray = selectedAttributes.map(attr => attr.value);
        const formData = new FormData();
        files.forEach((file) => formData.append("files", file));
        formData.append("attributes", JSON.stringify(attributeArray));

        try {
            let endpoint = "";
            switch (certificateType) {
                case "ID Card":
                    endpoint = "upload_id";
                    break;
                case "PAN Card":
                    endpoint = "upload_pan";
                    break;
                case "Aadhar Card":
                    endpoint = "upload_aadhar";
                    break;
                case "10th Marksheet":
                    endpoint = "upload_tenth";
                    break;
                case "12th Marksheet":
                    endpoint = "upload_twelth";
                    break;
                default:
                    endpoint = "upload_id"; 
            }

            const response = await axios.post(`http://localhost:3002/${endpoint}`, formData, {
              headers: { "Content-Type": "multipart/form-data" },
          });


            console.log("Response from server:", response.data);

            if (response.data.error) {
                setError(response.data.error);
            } else {
                setUploadedFiles([...uploadedFiles, ...files.map((file) => file.name)]);
                setExtractedData(response.data.extractedData);
                setDownloadLink(response.data.downloadLink);
            }
        } catch (err) {
            console.error("Upload Error:", err);
            setError("Error processing the files. Please try again.");
        } finally {
            setLoading(false);
        }
    };

  return (
    <div className="app">
      {page === 1 && (
        <div className="welcome-page">
          <img
      src="/image.png"
      alt="OCR Extraction Logo"
      className="logo"
      style={{
        width: '5cm',
        height: '5cm',
        objectFit: 'cover',
        borderRadius: '0',
      }}
    />
          <h1 className="welcome-title">Welcome to OCR Data Extraction</h1>
          <div className="p-4 bg-gray-100 rounded-lg shadow-md">
      <h2 className="text-lg font-semibold mb-2">Instructions to Use</h2>
      <br />
      <ul className="pl-5 space-y-1 text-left list-none">
        <h4>1. Upload clear PDFs</h4>
        <br />
        <h4>2. Old and handwritten documents should not be uploaded</h4>
        <br />
        <h4>3. Select the attributes or "All" option</h4>
        <br />
        <h4>4. Click on Upload to extract your attributes</h4>
        <br />
        <h4>5. Download extracted attributes as Excel or copy from the JSON text displayed</h4>

      </ul>

    </div>
    <br />
          <button className="continue-button" onClick={() => setPage(2)}>Continue</button>

          
        </div>
      )}

      {page === 2 && (
        <div className="selection-page">
          <h2 className="selection-title">Choose Your Id or Certificate Type</h2>
          <div className="certificate-options">
            <button onClick={() => { setCertificateType("ID Card"); setPage(3); }}>ID Card</button>
            <button onClick={() => { setCertificateType("Aadhar Card"); setPage(5); }}>Aadhar Card</button>
            <button onClick={() => { setCertificateType("10th Marksheet"); setPage(6); }}>10th Marksheet</button>
            <button onClick={() => { setCertificateType("12th Marksheet"); setPage(7); }}>12th Marksheet</button>
          </div>
        </div>
      )}

    {(page === 3 || page === 4 || page === 5 || page === 6 || page === 7) && (
        <div>
          <header className="app-header">
            <h1  >{certificateType} OCR Extractor</h1>
            <HomeIcon 
    className="home-button" 
    style={{ fontSize: "50px", color: "white" }} 
    onClick={handleRefresh} 
/>
          </header>

          <div className="container">
            
            <div className="upload-section">
              <h2>Upload {certificateType} PDFs</h2>
              <input type="file" multiple onChange={handleFileChange} className="file-input" />

              {files.length > 0 && (
                <div className="file-list">
                  <h3>Selected Files:</h3>
                  <div className="file-scroll">
                    {files.map((file, index) => (
                      <div key={index} className="file-item">
                        <span>{file.name}</span>
                        <button className="delete-button" onClick={() => handleDeleteFile(index)}>Delete</button>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="dropdown-section">
                <h3>Select Attributes:</h3>
                {/* <Select
                            options={
                                {
                                    "PAN Card": panCardAttributes,
                                    "ID Card": idCardAttributes,
                                    "Aadhar Card": aadharCardAttributes,
                                    "10th Marksheet": tenthMarksheetAttributes,
                                    "12th Marksheet": twelthMarksheetAttributes
                                }[certificateType] // Dynamic options
                            }
                            isMulti
                            value={selectedAttributes}
                            onChange={setSelectedAttributes}
                            className="dropdown"
                            placeholder="Choose attributes..."
                        />
              </div> */
<Select
    options={[
        { value: "all", label: "All" }, // Adding "All" option at the top
        ...{
            "PAN Card": panCardAttributes,
            "ID Card": idCardAttributes,
            "Aadhar Card": aadharCardAttributes,
            "10th Marksheet": tenthMarksheetAttributes,
            "12th Marksheet": twelthMarksheetAttributes
        }[certificateType] // Existing options
    ]}
    isMulti
    value={selectedAttributes}
    onChange={(selected) => {
        const isAllSelected = selected.some(attr => attr.value === "all");

        if (isAllSelected) {
            const allAttributes = {
                "PAN Card": panCardAttributes,
                "ID Card": idCardAttributes,
                "Aadhar Card": aadharCardAttributes,
                "10th Marksheet": tenthMarksheetAttributes,
                "12th Marksheet": twelthMarksheetAttributes
            }[certificateType];

            // Ensure "All" + all other attributes are selected
            setSelectedAttributes(allAttributes);
        } else {
            setSelectedAttributes(selected);
        }
    }}
    className="dropdown"
    placeholder="Choose attributes..."
/>
}
</div>

              {error && <p className="error-message">{error}</p>}
              <button className="upload-button" onClick={handleFileUpload} disabled={loading}>
                {loading ? "Processing..." : "Upload & Extract"}
              </button>
            </div>

            {uploadedFiles.length > 0 && (
              <div className="uploaded-files-section">
                <h2>Uploaded Files</h2>
                <div className="uploaded-file-list">
                  {uploadedFiles.map((file, index) => (
                    <div key={index} className="uploaded-file-item">
                      <span>{file}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {extractedData.length > 0 && (
              <div className="result-container">
                <h2>Extracted Data</h2>
                {extractedData.map((data, index) => (
                  <div key={index} className="file-result">
                    <h3>{data.file}</h3>
                    <pre>{JSON.stringify(data.attributes, null, 2)}</pre>
                  </div>
                ))}
              </div>
            )}

            {downloadLink && (
              <div className="download-container">
                <h2>Download Extracted Data</h2>
                <a href={downloadLink} download className="download-link">
                  ⬇ Click here to download Excel file
                </a>
              </div>
            )}

            
          </div>
        </div>
      )}
    </div>
  );
}

export default App;