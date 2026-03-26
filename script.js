document.getElementById("calcBtn").addEventListener("click", async () => {
  const num1 = Number(document.getElementById("num1").value);
  const num2 = Number(document.getElementById("num2").value);
  const resultEl = document.getElementById("result");

  if (isNaN(num1) || isNaN(num2)) {
    resultEl.textContent = "결과: 숫자 2개를 입력하세요.";
    return;
  }

  try {
    const response = await fetch("/api/add", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ num1, num2 })
    });

    const data = await response.json();
    resultEl.textContent = `결과: ${data.result}`;
  } catch (error) {
    resultEl.textContent = "결과: 오류가 발생했습니다.";
    console.error(error);
  }
});
