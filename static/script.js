document.getElementById("gif-form").addEventListener("submit", async function (event) {
    event.preventDefault();
  
    const fileInput = document.getElementById("gif-file");
    const textInput = document.getElementById("text-input");
    const resultImg = document.getElementById("processed-gif");
  
    if (!fileInput.files.length || !textInput.value.trim()) {
      alert("Please upload a GIF and enter text.");
      return;
    }
  
    const formData = new FormData();
    formData.append("gif", fileInput.files[0]);
    formData.append("text", textInput.value);
  
    try {
      const response = await fetch("/process", {
        method: "POST",
        body: formData,
      });
  
      if (!response.ok) throw new Error("Error processing GIF");
  
      const result = await response.json();
      resultImg.src = `/processed/${result.filename}`;
      resultImg.style.display = "block";
    } catch (error) {
      alert("Failed to process GIF: " + error.message);
    }
  });
  