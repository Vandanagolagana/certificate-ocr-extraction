
const express = require("express");
const fs = require("fs");
const path = require("path");
const { spawn } = require("child_process");
const fileUpload = require("express-fileupload");
const cors = require("cors");
const xlsx = require("xlsx");

const app = express();
const port = 3002;

app.use(cors());
app.use(fileUpload());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

const uploadDir = path.join(__dirname, "uploads");
const outputJsonPath = path.join(__dirname, "extracted_data.json");
const outputExcelPath = path.join(__dirname, "extracted_data.xlsx");

if (!fs.existsSync(uploadDir)) {
    fs.mkdirSync(uploadDir);
}

const convertJsonToExcel = (jsonData, outputExcelPath) => {
    const allAttributes = new Set(["file"]); // Include file name

    jsonData.forEach(item => {
        Object.keys(item.attributes || {}).forEach(attr => allAttributes.add(attr));
    });

    const excelData = jsonData.map(item => {
        let row = { file: item.file };
        allAttributes.forEach(attr => {
            if (attr !== "file") {
                row[attr] = item.attributes[attr] || "";
            }
        });
        return row;
    });

    const worksheet = xlsx.utils.json_to_sheet(excelData, { header: Array.from(allAttributes) });
    const workbook = xlsx.utils.book_new();
    xlsx.utils.book_append_sheet(workbook, worksheet, "Extracted Data");
    xlsx.writeFile(workbook, outputExcelPath);
};

const processPdfsWithOcr = (filePaths, attributes, script, callback) => {
    const attributesJson = JSON.stringify(attributes);
    const pythonProcess = spawn("python", [script, ...filePaths, attributesJson]);

    let extractedData = "";
    let errorData = "";

    pythonProcess.stdout.on("data", (data) => {
        extractedData += data.toString();
    });

    pythonProcess.stderr.on("data", (data) => {
        errorData += data.toString();
        console.error("OCR Error:", data.toString());
    });

    pythonProcess.on("close", (code) => {
        console.log("Raw OCR Output:", extractedData);

        if (code !== 0) {
            console.error(`OCR Process exited with code ${code}, Errors: ${errorData}`);
            return callback(new Error(`OCR processing failed: ${errorData}`));
        }

        try {
            const jsonResponse = JSON.parse(extractedData);
            fs.writeFileSync(outputJsonPath, JSON.stringify(jsonResponse, null, 2));

            // Convert extracted JSON to Excel
            convertJsonToExcel(jsonResponse, outputExcelPath);

            callback(null, jsonResponse, outputExcelPath);
        } catch (error) {
            console.error("JSON Parse Error:", extractedData);
            callback(new Error("Invalid JSON format from OCR output."));
        }
    });
};

app.post("/upload_id", async (req, res) => {
    handleUpload(req, res, "server_pack/ocr_processor.py");
});

app.post("/upload_pan", async (req, res) => {
    handleUpload(req, res, "server_pack/pan_ocr_processor.py");
});

app.post("/upload_aadhar", async (req, res) => {
    handleUpload(req, res, "server_pack/aadhar_ocr_processor.py");
});
app.post("/upload_tenth", async (req, res) => {
    handleUpload(req, res, "server_pack/tenth_ocr_processor.py");
});
app.post("/upload_twelth", async (req, res) => {
    handleUpload(req, res, "server_pack/inter_ocr_processor.py");
});

const handleUpload = async (req, res, script) => {
    if (!req.files || !req.files.files) {
        return res.status(400).json({ error: "No files uploaded." });
    }

    const uploadedFiles = Array.isArray(req.files.files) ? req.files.files : [req.files.files];

    let attributes;
    try {
        attributes = JSON.parse(req.body.attributes);
    } catch (error) {
        return res.status(400).json({ error: "Invalid attributes JSON format." });
    }

    const filePaths = [];
    try {
        await Promise.all(
            uploadedFiles.map(async (file) => {
                const filePath = path.join(uploadDir, file.name);
                await file.mv(filePath);
                filePaths.push(filePath);
            })
        );

        processPdfsWithOcr(filePaths, attributes, script, (error, extractedData, excelFilePath) => {
            if (error) {
                console.error("OCR Processing Failed:", error.message);
                return res.status(500).json({ error: "OCR processing failed.", details: error.message });
            }

            res.json({
                message: "Files processed successfully with OCR!",
                extractedData,
                downloadLink: `http://localhost:${port}/download/extracted_data.xlsx`
            });
        });
    } catch (error) {
        console.error("File Save Error:", error.message);
        res.status(500).json({ error: "Error saving files.", details: error.message });
    }
};



// Serve the Excel file for download
app.get("/download/extracted_data.xlsx", (req, res) => {
    if (fs.existsSync(outputExcelPath)) {
        res.download(outputExcelPath);
    } else {
        res.status(404).json({ error: "Extracted Excel file not found." });
    }
});

app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}`);
});
