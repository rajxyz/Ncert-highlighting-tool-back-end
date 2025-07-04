chapterSelect.addEventListener("change", function () {
  const book = bookSelect.value;
  const chapter = chapterSelect.value;

  if (book !== "none" && chapter !== "none") {
    fetch("https://ncert-highlighting-tool-back-end.onrender.com/api/load_chapter", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ book, chapter })
    })
    .then(response => response.json())
    .then(data => {
      const contentArea = document.getElementById("content-area");
      contentArea.innerHTML = "";

      if (data.pages && data.pages.length > 0) {
        data.pages.forEach(img => {
          const imgElem = document.createElement("img");
          imgElem.src = img;
          imgElem.style.width = "100%";
          imgElem.style.marginBottom = "20px";
          contentArea.appendChild(imgElem);
        });
      } else {
        contentArea.innerHTML = "<p>No images found for this chapter.</p>";
      }
    })
    .catch(error => {
      console.error("Error loading chapter:", error);
      document.getElementById("content-area").innerHTML =
        "<p>Error loading chapter content.</p>";
    });
  }
});
