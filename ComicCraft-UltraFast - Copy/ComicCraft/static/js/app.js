function showLoading() {
  const button = document.getElementById("generate-button");
  const loading = document.getElementById("loading");
  if (button) {
    button.disabled = true;
    button.textContent = "Creating comic…";
  }
  if (loading) loading.hidden = false;
}
