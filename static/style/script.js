function highlightTeam(teamId) {
    document.querySelectorAll('.team').forEach(team => {
        team.classList.remove('highlighted');
    });
    const selectedTeam = document.getElementById(`team-${teamId}`);
    if (selectedTeam) {
        selectedTeam.classList.add('highlighted');
    }
}

function showTeamDetails(teamId, teamNo, event) {
    event.stopPropagation();
    
    fetch(`/get-scs-by-team/${teamId}/`)
        .then(response => response.json())
        .then(data => {
            const popup = document.getElementById('popup');
            const popupText = document.getElementById('popup-text');
            let content = `<h2>STORE ALLOCATION OF ${teamNo}</h2>`;
            
            // Track already allocated stores
            const allocatedStores = data.allocated_stores || [];
            
            if (data.scs && data.scs.length > 0) {
                data.scs.forEach(sc => {
                    const storeCount = sc.store_ids ? sc.store_ids.length : 0;
                    content += `
                        <div class="sc-container">
                            <div class="detail-store sc" data-consultant-id="${sc.id}">
                                ${sc.name}
                                <span class="store-count-popup" style="background-color: #4CAF50; color: white; border-radius: 4px; padding: 5px; margin-left: 10px;">
                                    ${storeCount}
                                </span>
                            </div>
                            <div class="detail-body">
                                <select id="id_store_id_${sc.id}" class="form-control store-select" name="store_id[]" multiple="multiple">
                                    <option value="" disabled>------</option>
                                    {% for store_consultant in store_consultants %}
                                    <option
                                        style="background-color: #673ab7; color: white;"
                                        value="{{ store_consultant.store_id }}"
                                        {% if store_consultant.store_id in allocatedStores %}disabled{% endif %}>
                                        {{ store_consultant.store_id }} - {{ store_consultant.store_name }}
                                    </option>
                                    {% endfor %}
                                </select>
                            </div>
                        </div>`;
                });
            } else {
                content += `<p>No consultants assigned</p>`;
            }
            
            content += `<button id="saveBtn" style="background-color: #4CAF50; color: white; border-radius: 4px; padding: 10px 20px;" onclick="saveConsultantStores()">Save</button>`;
            popupText.innerHTML = content;
            popup.style.display = 'block';
            
            data.scs.forEach(sc => {
                setTimeout(() => {
                    $(`#id_store_id_${sc.id}`).select2({
                        width: '100%',
                        placeholder: "Select Store IDs",
                        allowClear: true,
                        tags: true
                    });
                    
                    const savedStoreIds = sc.store_ids;
                    $(`#id_store_id_${sc.id}`).val(savedStoreIds).trigger('change');
                }, 100);
            });
        })
        .catch(error => {
            console.error('Error fetching SC details:', error);
            alert('Failed to load SC details. Please try again.');
        });
}

function closePopup() {
    document.getElementById('popup').style.display = 'none';
}

window.onclick = function (event) {
    const popup = document.getElementById('popup');
    if (event.target === popup) {
        popup.style.display = 'none';
    }
};

function fetchAllocationsAndRender() {
    return fetch('/get-allocations/')
        .then(response => response.json())
        .then(data => {
            data.forEach(allocation => {
                const consultantElement = document.getElementById(`sc${allocation.consultant__id}`);
                const areaElement = document.querySelector(`[data-area-id="${allocation.area__id}"]`);
                if (consultantElement && areaElement) {
                    const targetContainer = areaElement.querySelector('.team-body') || areaElement;
                    targetContainer.appendChild(consultantElement);
                }
            });
            updateScCounts();
        })
        .catch(error => console.error('Error fetching allocations:', error));
}

function allowDrop(event) {
    event.preventDefault();
}

function drag(event) {
    event.dataTransfer.setData("text", event.target.id);
}

function drop(event) {
    event.preventDefault();
    const data = event.dataTransfer.getData("text");
    const consultantElement = document.getElementById(data);
    let target = event.target.closest('.team-body, .not-allocated-body');
    if (target) {
        target.appendChild(consultantElement);
        updateScCounts();
        saveCurrentStateToLocal();
    }
}

function saveCurrentStateToLocal() {
    const allocations = [];
    document.querySelectorAll('.team-body, .not-allocated-body').forEach(area => {
        const areaId = area.getAttribute('data-area-id') || 'not-allocated';
        area.querySelectorAll('.sc').forEach(consultant => {
            allocations.push({
                consultantId: consultant.getAttribute('data-consultant-id'),
                areaId: areaId
            });
        });
    });
    localStorage.setItem('allocations', JSON.stringify(allocations));
}

function saveAllocations() {
    const year = document.getElementById('year-select').value;
    const month = document.getElementById('month-select').value;
    const allocations = [];
    
    document.querySelectorAll('.team-body, .not-allocated-body').forEach(area => {
        const areaId = area.getAttribute('data-area-id') || 'not-allocated';
        area.querySelectorAll('.sc').forEach(consultant => {
            allocations.push({
                consultantId: consultant.getAttribute('data-consultant-id'),
                areaId: areaId
            });
        });
    });
    
    fetch('/save-allocations/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({allocations, year, month})
    })
        .then(response => response.json())
        .then(data => {
            alert('Allocations saved successfully!');
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Failed to save the allocations. Please try again.');
        });
}

function updateScCounts() {
    document.querySelectorAll('.team').forEach(team => {
        const count = team.querySelectorAll('.sc').length;
        team.querySelector('.sc-count').textContent = count;
    });
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
