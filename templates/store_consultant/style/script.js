function showTeamDetails(teamId, teamNo, event) {
    event.stopPropagation();
    fetch(`/get-scs-by-team/${teamId}/`)
        .then((response) => response.json())
        .then((data) => {
            const popup = document.getElementById("popup");
            const popupText = document.getElementById("popup-text");
            
            let content = `<h2>Team Details for ${teamNo}</h2>`;
            data.scs.forEach((sc) => {
                content += `
                <div>
                    ${sc.name} - Store IDs: ${sc.store_ids.join(", ")}
                </div>`;
            });
            popupText.innerHTML = content;
            popup.style.display = "block";
        })
        .catch((error) => console.error("Error fetching team details:", error));
}

function closePopup() {
    document.getElementById("popup").style.display = "none";
}

function saveAllocations() {
    const allocations = [];
    document.querySelectorAll(".team-body").forEach((body) => {
        const teamId = body.dataset.areaId;
        body.querySelectorAll(".sc").forEach((consultant) => {
            allocations.push({
                teamId: teamId,
                consultantId: consultant.dataset.consultantId,
            });
        });
    });
    
    fetch("/save-allocations/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken"),
        },
        body: JSON.stringify({allocations}),
    })
        .then((response) => response.json())
        .then((data) => {
            if (data.status === "success") {
                alert("Allocations saved successfully!");
            } else {
                alert("Error saving allocations.");
            }
        })
        .catch((error) => console.error("Error saving allocations:", error));
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === name + "=") {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
