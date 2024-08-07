import React, { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Box, Button, Typography, List, ListItem, Paper, IconButton } from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import DeleteIcon from '@mui/icons-material/Delete';
import axios from 'axios';
// import './FileUpload.css'; // For any additional styling

const FileUpload: React.FC = () => {
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
  const { getRootProps, getInputProps } = useDropzone({
    onDrop: (acceptedFiles: File[]) => {
      setUploadedFiles((prevFiles) => [...prevFiles, ...acceptedFiles]);
      handleUpload(acceptedFiles);
    },
  });

  const handleUpload = (files: File[]) => {
    const formData = new FormData();
    files.forEach((file) => {
      formData.append('file', file);
    });

    axios.post('http://localhost:5000/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    .then((response) => {
      console.log('File uploaded successfully:', response.data);
    })
    .catch((error) => {
      console.error('Error uploading file:', error);
    });
  };

  const handleRemoveFile = (fileName: string, event: React.MouseEvent) => {
    event.stopPropagation(); // Stop the click event from propagating
    setUploadedFiles((prevFiles) => prevFiles.filter(file => file.name !== fileName));
  };

  return (
    <Box
      display="flex"
      flexDirection="column"
      alignItems="center"
      justifyContent="center"
      p={4}
      bgcolor="#ffffff"
      minHeight="100vh"
      sx={{ fontFamily: "'Open Sans', 'Source Sans 3', sans-serif" }}
    >
      <Typography variant="h4" component="h1" gutterBottom>
        UF Automatic Scheduler and Optimizer
      </Typography>
      <Box
        display="flex"
        flexDirection="column"
        alignItems="center"
        justifyContent="center"
        p={4}
        bgcolor="#e3f2fd"
        borderRadius={2}
        boxShadow={3}
        {...getRootProps()}
        border="2px dashed #90caf9"
        maxWidth="600px"
        width="100%"
        minHeight="250px"
        marginBottom="20px"
        sx={{ fontFamily: "'Open Sans', 'Source Sans 3', sans-serif" }}
      >
        <input {...getInputProps()} />
        <CloudUploadIcon style={{ fontSize: 40, color: '#42a5f5' }} />
        <Typography variant="h6" color="textSecondary" gutterBottom>
          Drag and drop files here or click to browse
        </Typography>
        <Typography variant="body2" color="textSecondary">
          PNG, JPG, GIF, MP4 (max 1MB)
        </Typography>
        <Paper variant="outlined" style={{ width: '100%', marginTop: 10, maxHeight: 150, overflow: 'auto' }}>
          <List>
            {uploadedFiles.map((file) => (
              <ListItem key={file.name} style={{ display: 'flex', justifyContent: 'space-between' }}>
                {file.name}
                <IconButton edge="end" aria-label="delete" onClick={(event) => handleRemoveFile(file.name, event)}>
                  <DeleteIcon />
                </IconButton>
              </ListItem>
            ))}
          </List>
        </Paper>
      </Box>
      <Button variant="contained" color="primary">
        Upload
      </Button>
    </Box>
  );
};

export default FileUpload;
