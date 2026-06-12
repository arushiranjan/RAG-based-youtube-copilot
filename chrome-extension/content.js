async function initSidebar() {

    const sidebar = document.createElement("div");
    sidebar.id = "yt-copilot";

    const htmlUrl = chrome.runtime.getURL("sidebar.html");

    const response = await fetch(htmlUrl);

    sidebar.innerHTML = await response.text();

    document.body.appendChild(sidebar);

    const videoId =
        new URL(window.location.href)
        .searchParams.get("v");

    console.log(videoId);

    fetch(
        "http://localhost:8000/process-video",
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                video_id: videoId
            })
        }
    )
    .then(res => res.json())
    .then(data => {
        console.log(data);
    })
    .catch(err => {
        console.error(err);
    });

    document
        .getElementById("closeBtn")
        .addEventListener("click", () => {
            sidebar.remove();
        });

    document
        .getElementById("askBtn")
        .addEventListener("click", async () => {

            const question =
                document.getElementById("question").value;

            const responseBox =
                document.getElementById("response");

            responseBox.innerHTML = `
                <div class="loader"></div>
                Thinking...
            `;

            try {

                const response =
                    await fetch(
                        "http://localhost:8000/ask",
                        {
                            method: "POST",
                            headers: {
                                "Content-Type": "application/json"
                            },
                            body: JSON.stringify({
                                video_id: videoId,
                                question: question
                            })
                        }
                    );

                const data =
                    await response.json();

                responseBox.innerText =
                    data.answer;

            } catch (error) {

                responseBox.innerText =
                    "❌ Backend not running.";

                console.error(error);
            }
        });
}

initSidebar();