// Admin Panel JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Check if user is logged in
    checkLoginStatus();
    
    // Login form submission
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
    
    // Logout button
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', handleLogout);
    }
    
    // Site settings form
    const siteSettingsForm = document.getElementById('site-settings-form');
    if (siteSettingsForm) {
        siteSettingsForm.addEventListener('submit', handleSiteSettingsUpdate);
    }
    
    // Add match form
    const saveMatchBtn = document.getElementById('save-match-btn');
    if (saveMatchBtn) {
        saveMatchBtn.addEventListener('click', handleAddMatch);
    }
    
    // Update match button
    const updateMatchBtn = document.getElementById('update-match-btn');
    if (updateMatchBtn) {
        updateMatchBtn.addEventListener('click', handleUpdateMatch);
    }
    
    // Add result button
    const saveResultBtn = document.getElementById('save-result-btn');
    if (saveResultBtn) {
        saveResultBtn.addEventListener('click', handleAddResult);
    }
    
    // Update result button
    const updateResultBtn = document.getElementById('update-result-btn');
    if (updateResultBtn) {
        updateResultBtn.addEventListener('click', handleUpdateResult);
    }
    
    // Match filter for results
    const resultMatchFilter = document.getElementById('result-match-filter');
    if (resultMatchFilter) {
        resultMatchFilter.addEventListener('change', function() {
            loadMatchResults(this.value);
        });
    }
});

// Check if user is logged in
function checkLoginStatus() {
    const token = localStorage.getItem('admin_token');
    const username = localStorage.getItem('admin_username');
    
    if (token && username) {
        // Show admin content, hide login form
        document.getElementById('login-container').classList.add('d-none');
        document.getElementById('admin-content').classList.remove('d-none');
        
        // Load admin data
        loadDashboardData();
        loadMatches();
        loadTeams();
        loadMatchResults();
        loadSiteSettings();
    } else {
        // Show login form, hide admin content
        document.getElementById('login-container').classList.remove('d-none');
        document.getElementById('admin-content').classList.add('d-none');
    }
}

// Handle login
function handleLogin(event) {
    event.preventDefault();
    
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    
    fetch('/api/admin/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert('Login failed: ' + data.error);
        } else {
            // Store login info in localStorage
            localStorage.setItem('admin_token', 'dummy_token'); // In a real app, use the token from the server
            localStorage.setItem('admin_username', username);
            
            // Show admin content
            checkLoginStatus();
        }
    })
    .catch(error => {
        console.error('Error during login:', error);
        alert('An error occurred during login. Please try again.');
    });
}

// Handle logout
function handleLogout() {
    // Clear localStorage
    localStorage.removeItem('admin_token');
    localStorage.removeItem('admin_username');
    
    // Show login form
    checkLoginStatus();
}

// Load dashboard data
function loadDashboardData() {
    // Load total teams
    fetch('/api/teams/')
        .then(response => response.json())
        .then(teams => {
            document.getElementById('total-teams').textContent = teams.length;
            
            // Load top teams
            const topTeamsList = document.getElementById('top-teams-list');
            if (topTeamsList) {
                if (teams.length === 0) {
                    topTeamsList.innerHTML = '<p>No teams registered yet</p>';
                } else {
                    // Sort teams by rank
                    teams.sort((a, b) => (a.rank || 999) - (b.rank || 999));
                    
                    let html = '<ul class="list-group">';
                    teams.slice(0, 10).forEach(team => {
                        html += `
                            <li class="list-group-item d-flex justify-content-between align-items-center">
                                ${team.name}
                                <span class="badge bg-primary rounded-pill">${team.total_points || 0} pts</span>
                            </li>
                        `;
                    });
                    html += '</ul>';
                    topTeamsList.innerHTML = html;
                }
            }
        })
        .catch(error => {
            console.error('Error loading teams:', error);
            document.getElementById('total-teams').textContent = 'Error';
        });
    
    // Load upcoming matches
    fetch('/api/matches/upcoming')
        .then(response => response.json())
        .then(matches => {
            document.getElementById('upcoming-matches').textContent = matches.length;
        })
        .catch(error => {
            console.error('Error loading upcoming matches:', error);
            document.getElementById('upcoming-matches').textContent = 'Error';
        });
    
    // Load live matches
    fetch('/api/matches/live')
        .then(response => response.json())
        .then(matches => {
            document.getElementById('live-matches').textContent = matches.length;
        })
        .catch(error => {
            console.error('Error loading live matches:', error);
            document.getElementById('live-matches').textContent = 'Error';
        });
    
    // Load all matches for recent matches list
    fetch('/api/matches/')
        .then(response => response.json())
        .then(matches => {
            const recentMatchesList = document.getElementById('recent-matches-list');
            if (recentMatchesList) {
                if (matches.length === 0) {
                    recentMatchesList.innerHTML = '<p>No matches scheduled yet</p>';
                } else {
                    // Sort matches by date (newest first)
                    matches.sort((a, b) => new Date(b.match_date) - new Date(a.match_date));
                    
                    let html = '<ul class="list-group">';
                    matches.slice(0, 5).forEach(match => {
                        const matchDate = new Date(match.match_date);
                        html += `
                            <li class="list-group-item d-flex justify-content-between align-items-center">
                                <div>
                                    <div>${match.name}</div>
                                    <small class="text-muted">${formatDate(matchDate)}</small>
                                </div>
                                <span class="badge bg-${getStatusBadgeColor(match.status)}">${match.status}</span>
                            </li>
                        `;
                    });
                    html += '</ul>';
                    recentMatchesList.innerHTML = html;
                }
            }
        })
        .catch(error => {
            console.error('Error loading matches:', error);
            const recentMatchesList = document.getElementById('recent-matches-list');
            if (recentMatchesList) {
                recentMatchesList.innerHTML = '<p>Error loading matches</p>';
            }
        });
}

// Load matches
function loadMatches() {
    fetch('/api/matches/')
        .then(response => response.json())
        .then(matches => {
            const matchesTableBody = document.getElementById('matches-table-body');
            if (matchesTableBody) {
                if (matches.length === 0) {
                    matchesTableBody.innerHTML = '<tr><td colspan="7" class="text-center">No matches found</td></tr>';
                } else {
                    let html = '';
                    matches.forEach(match => {
                        const matchDate = new Date(match.match_date);
                        html += `
                            <tr>
                                <td>${match.id}</td>
                                <td>${match.name}</td>
                                <td>${formatDate(matchDate)}</td>
                                <td>${match.map_name}</td>
                                <td><span class="badge bg-${getStatusBadgeColor(match.status)}">${match.status}</span></td>
                                <td>${match.youtube_link ? '<a href="' + match.youtube_link + '" target="_blank">Link</a>' : 'N/A'}</td>
                                <td>
                                    <div class="action-buttons">
                                        <button class="btn btn-sm btn-primary" onclick="editMatch(${match.id})">Edit</button>
                                        <button class="btn btn-sm btn-danger" onclick="deleteMatch(${match.id})">Delete</button>
                                    </div>
                                </td>
                            </tr>
                        `;
                    });
                    matchesTableBody.innerHTML = html;
                }
            }
            
            // Also populate match dropdowns for results
            populateMatchDropdowns(matches);
        })
        .catch(error => {
            console.error('Error loading matches:', error);
            const matchesTableBody = document.getElementById('matches-table-body');
            if (matchesTableBody) {
                matchesTableBody.innerHTML = '<tr><td colspan="7" class="text-center">Error loading matches</td></tr>';
            }
        });
}

// Load teams
function loadTeams() {
    fetch('/api/teams/')
        .then(response => response.json())
        .then(teams => {
            const teamsTableBody = document.getElementById('teams-table-body');
            if (teamsTableBody) {
                if (teams.length === 0) {
                    teamsTableBody.innerHTML = '<tr><td colspan="8" class="text-center">No teams found</td></tr>';
                } else {
                    let html = '';
                    teams.forEach(team => {
                        const registrationDate = new Date(team.registration_date);
                        html += `
                            <tr>
                                <td>${team.id}</td>
                                <td><img src="${team.logo_path}" alt="${team.name} Logo" class="team-logo-thumbnail"></td>
                                <td>${team.name}</td>
                                <td>${team.captain_name}</td>
                                <td>${formatDate(registrationDate)}</td>
                                <td>${team.total_points || 0}</td>
                                <td>${team.rank || 'N/A'}</td>
                                <td>
                                    <div class="action-buttons">
                                        <button class="btn btn-sm btn-info" onclick="viewTeamDetails(${team.id})">Details</button>
                                        <button class="btn btn-sm btn-primary" onclick="editTeam(${team.id})">Edit</button>
                                        <button class="btn btn-sm btn-danger" onclick="deleteTeam(${team.id})">Delete</button>
                                    </div>
                                </td>
                            </tr>
                        `;
                    });
                    teamsTableBody.innerHTML = html;
                }
            }
            
            // Also populate team dropdowns for results
            populateTeamDropdowns(teams);
        })
        .catch(error => {
            console.error('Error loading teams:', error);
            const teamsTableBody = document.getElementById('teams-table-body');
            if (teamsTableBody) {
                teamsTableBody.innerHTML = '<tr><td colspan="8" class="text-center">Error loading teams</td></tr>';
            }
        });
}

// Load match results
function loadMatchResults(matchId = '') {
    let url = '/api/admin/results';
    if (matchId) {
        url += `?match_id=${matchId}`;
    }
    
    fetch(url)
        .then(response => response.json())
        .then(results => {
            const resultsTableBody = document.getElementById('results-table-body');
            if (resultsTableBody) {
                if (results.length === 0) {
                    resultsTableBody.innerHTML = '<tr><td colspan="7" class="text-center">No results found</td></tr>';
                } else {
                    let html = '';
                    results.forEach(result => {
                        html += `
                            <tr>
                                <td>${result.id}</td>
                                <td>${result.match_name}</td>
                                <td>${result.team_name}</td>
                                <td>${result.position || 'N/A'}</td>
                                <td>${result.kills}</td>
                                <td>${result.points}</td>
                                <td>
                                    <div class="action-buttons">
                                        <button class="btn btn-sm btn-primary" onclick="editResult(${result.id})">Edit</button>
                                        <button class="btn btn-sm btn-danger" onclick="deleteResult(${result.id})">Delete</button>
                                    </div>
                                </td>
                            </tr>
                        `;
                    });
                    resultsTableBody.innerHTML = html;
                }
            }
        })
        .catch(error => {
            console.error('Error loading results:', error);
            const resultsTableBody = document.getElementById('results-table-body');
            if (resultsTableBody) {
                resultsTableBody.innerHTML = '<tr><td colspan="7" class="text-center">Error loading results</td></tr>';
            }
        });
}

// Load site settings
function loadSiteSettings() {
    fetch('/api/config/')
        .then(response => response.json())
        .then(config => {
            document.getElementById('site-title').value = config.site_title || '';
            document.getElementById('donation-link').value = config.donation_link || '';
            document.getElementById('youtube-channel').value = config.youtube_channel || '';
            document.getElementById('banner-image').value = config.banner_image || '';
            document.getElementById('logo-image').value = config.logo_image || '';
        })
        .catch(error => {
            console.error('Error loading site settings:', error);
            alert('Error loading site settings. Please try again.');
        });
}

// Handle site settings update
function handleSiteSettingsUpdate(event) {
    event.preventDefault();
    
    const siteTitle = document.getElementById('site-title').value;
    const donationLink = document.getElementById('donation-link').value;
    const youtubeChannel = document.getElementById('youtube-channel').value;
    const bannerImage = document.getElementById('banner-image').value;
    const logoImage = document.getElementById('logo-image').value;
    
    fetch('/api/admin/config', {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            site_title: siteTitle,
            donation_link: donationLink,
            youtube_channel: youtubeChannel,
            banner_image: bannerImage,
            logo_image: logoImage
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert('Error: ' + data.error);
        } else {
            alert('Site settings updated successfully!');
        }
    })
    .catch(error => {
        console.error('Error updating site settings:', error);
        alert('An error occurred while updating site settings. Please try again.');
    });
}

// Handle add match
function handleAddMatch() {
    const matchName = document.getElementById('match-name').value;
    const matchDate = document.getElementById('match-date').value;
    const matchMap = document.getElementById('match-map').value;
    const matchStatus = document.getElementById('match-status').value;
    const matchYoutube = document.getElementById('match-youtube').value;
    
    if (!matchName || !matchDate || !matchMap || !matchStatus) {
        alert('Please fill in all required fields.');
        return;
    }
    
    fetch('/api/admin/matches', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            name: matchName,
            match_date: matchDate,
            map_name: matchMap,
            status: matchStatus,
            youtube_link: matchYoutube
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert('Error: ' + data.error);
        } else {
            alert('Match created successfully!');
            // Close modal and reset form
            const modal = bootstrap.Modal.getInstance(document.getElementById('addMatchModal'));
            modal.hide();
            document.getElementById('add-match-form').reset();
            // Reload matches
            loadMatches();
            loadDashboardData();
        }
    })
    .catch(error => {
        console.error('Error creating match:', error);
        alert('An error occurred while creating the match. Please try again.');
    });
}

// Edit match
function editMatch(matchId) {
    fetch(`/api/matches/${matchId}`)
        .then(response => response.json())
        .then(match => {
            document.getElementById('edit-match-id').value = match.id;
            document.getElementById('edit-match-name').value = match.name;
            
            // Format date for datetime-local input
            const matchDate = new Date(match.match_date);
            const formattedDate = matchDate.toISOString().slice(0, 16);
            document.getElementById('edit-match-date').value = formattedDate;
            
            document.getElementById('edit-match-map').value = match.map_name;
            document.getElementById('edit-match-status').value = match.status;
            document.getElementById('edit-match-youtube').value = match.youtube_link || '';
            
            // Show modal
            const modal = new bootstrap.Modal(document.getElementById('editMatchModal'));
            modal.show();
        })
        .catch(error => {
            console.error('Error fetching match details:', error);
            alert('Error fetching match details. Please try again.');
        });
}

// Handle update match
function handleUpdateMatch() {
    const matchId = document.getElementById('edit-match-id').value;
    const matchName = document.getElementById('edit-match-name').value;
    const matchDate = document.getElementById('edit-match-date').value;
    const matchMap = document.getElementById('edit-match-map').value;
    const matchStatus = document.getElementById('edit-match-status').value;
    const matchYoutube = document.getElementById('edit-match-youtube').value;
    
    if (!matchName || !matchDate || !matchMap || !matchStatus) {
        alert('Please fill in all required fields.');
        return;
    }
    
    fetch(`/api/admin/matches/${matchId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            name: matchName,
            match_date: matchDate,
            map_name: matchMap,
            status: matchStatus,
            youtube_link: matchYoutube
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert('Error: ' + data.error);
        } else {
            alert('Match updated successfully!');
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('editMatchModal'));
            modal.hide();
            // Reload matches
            loadMatches();
            loadDashboardData();
        }
    })
    .catch(error => {
        console.error('Error updating match:', error);
        alert('An error occurred while updating the match. Please try again.');
    });
}

// Handle add result
function handleAddResult() {
    const matchId = document.getElementById('result-match').value;
    const teamId = document.getElementById('result-team').value;
    const position = document.getElementById('result-position').value;
    const kills = document.getElementById('result-kills').value;
    const points = document.getElementById('result-points').value;
    
    if (!matchId || !teamId || !position || !kills || !points) {
        alert('Please fill in all required fields.');
        return;
    }
    
    fetch('/api/admin/results', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            match_id: parseInt(matchId),
            team_id: parseInt(teamId),
            position: parseInt(position),
            kills: parseInt(kills),
            points: parseInt(points)
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert('Error: ' + data.error);
        } else {
            alert('Match result added successfully!');
            // Close modal and reset form
            const modal = bootstrap.Modal.getInstance(document.getElementById('addResultModal'));
            modal.hide();
            document.getElementById('add-result-form').reset();
            // Reload results
            loadMatchResults();
            // Reload teams to update rankings
            loadTeams();
            loadDashboardData();
        }
    })
    .catch(error => {
        console.error('Error adding match result:', error);
        alert('An error occurred while adding the match result. Please try again.');
    });
}

// Edit result
function editResult(resultId) {
    fetch(`/api/admin/results/${resultId}`)
        .then(response => response.json())
        .then(result => {
            document.getElementById('edit-result-id').value = result.id;
            document.getElementById('edit-result-match').value = result.match_name;
            document.getElementById('edit-result-team').value = result.team_name;
            document.getElementById('edit-result-position').value = result.position || '';
            document.getElementById('edit-result-kills').value = result.kills;
            document.getElementById('edit-result-points').value = result.points;
            
            // Show modal
            const modal = new bootstrap.Modal(document.getElementById('editResultModal'));
            modal.show();
        })
        .catch(error => {
            console.error('Error fetching result details:', error);
            alert('Error fetching result details. Please try again.');
        });
}

// Handle update result
function handleUpdateResult() {
    const resultId = document.getElementById('edit-result-id').value;
    const position = document.getElementById('edit-result-position').value;
    const kills = document.getElementById('edit-result-kills').value;
    const points = document.getElementById('edit-result-points').value;
    
    if (!position || !kills || !points) {
        alert('Please fill in all required fields.');
        return;
    }
    
    fetch(`/api/admin/results/${resultId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            position: parseInt(position),
            kills: parseInt(kills),
            points: parseInt(points)
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert('Error: ' + data.error);
        } else {
            alert('Match result updated successfully!');
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('editResultModal'));
            modal.hide();
            // Reload results
            loadMatchResults();
            // Reload teams to update rankings
            loadTeams();
            loadDashboardData();
        }
    })
    .catch(error => {
        console.error('Error updating match result:', error);
        alert('An error occurred while updating the match result. Please try again.');
    });
}

// Populate match dropdowns
function populateMatchDropdowns(matches) {
    const resultMatch = document.getElementById('result-match');
    const resultMatchFilter = document.getElementById('result-match-filter');
    
    if (resultMatch) {
        resultMatch.innerHTML = '<option value="">Select Match</option>';
        matches.forEach(match => {
            resultMatch.innerHTML += `<option value="${match.id}">${match.name}</option>`;
        });
    }
    
    if (resultMatchFilter) {
        resultMatchFilter.innerHTML = '<option value="">All Matches</option>';
        matches.forEach(match => {
            resultMatchFilter.innerHTML += `<option value="${match.id}">${match.name}</option>`;
        });
    }
}

// Populate team dropdowns
function populateTeamDropdowns(teams) {
    const resultTeam = document.getElementById('result-team');
    
    if (resultTeam) {
        resultTeam.innerHTML = '<option value="">Select Team</option>';
        teams.forEach(team => {
            resultTeam.innerHTML += `<option value="${team.id}">${team.name}</option>`;
        });
    }
}

// View team details
function viewTeamDetails(teamId) {
    fetch(`/api/teams/${teamId}`)
        .then(response => response.json())
        .then(team => {
            let playersInfo = '';
            if (team.players && team.players.length > 0) {
                playersInfo = '<h5>Players:</h5><ul>';
                team.players.forEach(player => {
                    playersInfo += `<li>${player.name}</li>`;
                });
                playersInfo += '</ul>';
            } else {
                playersInfo = '<p>No players registered for this team.</p>';
            }
            
            alert(`
Team Details:
Name: ${team.name}
Captain: ${team.captain_name}
Contact: ${team.contact_info}
Registration Date: ${formatDate(new Date(team.registration_date))}
Total Points: ${team.total_points || 0}
Rank: ${team.rank || 'N/A'}

${playersInfo}
            `);
        })
        .catch(error => {
            console.error('Error fetching team details:', error);
            alert('Error fetching team details. Please try again.');
        });
}

// Helper function to format dates
function formatDate(date) {
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

// Helper function to get badge color based on status
function getStatusBadgeColor(status) {
    switch (status) {
        case 'scheduled':
            return 'primary';
        case 'live':
            return 'danger';
        case 'completed':
            return 'success';
        case 'cancelled':
            return 'secondary';
        default:
            return 'info';
    }
}

// Delete match function
function deleteMatch(matchId) {
    if (confirm('Are you sure you want to delete this match? This action cannot be undone.')) {
        fetch(`/api/admin/matches/${matchId}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert('Error: ' + data.error);
            } else {
                alert('Match deleted successfully!');
                // Reload matches
                loadMatches();
                loadDashboardData();
            }
        })
        .catch(error => {
            console.error('Error deleting match:', error);
            alert('An error occurred while deleting the match. Please try again.');
        });
    }
}

// Edit team function
function editTeam(teamId) {
    fetch(`/api/teams/${teamId}`)
        .then(response => response.json())
        .then(team => {
            // Create a modal for editing team
            let modalHTML = `
                <div class="modal fade" id="editTeamModal" tabindex="-1" aria-hidden="true">
                    <div class="modal-dialog">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title">Edit Team</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                            </div>
                            <div class="modal-body">
                                <form id="edit-team-form">
                                    <input type="hidden" id="edit-team-id" value="${team.id}">
                                    <div class="mb-3">
                                        <label for="edit-team-name" class="form-label">Team Name</label>
                                        <input type="text" class="form-control" id="edit-team-name" value="${team.name}" required>
                                    </div>
                                    <div class="mb-3">
                                        <label for="edit-captain-name" class="form-label">Captain Name</label>
                                        <input type="text" class="form-control" id="edit-captain-name" value="${team.captain_name}" required>
                                    </div>
                                    <div class="mb-3">
                                        <label for="edit-contact-info" class="form-label">Contact Information</label>
                                        <input type="text" class="form-control" id="edit-contact-info" value="${team.contact_info}" required>
                                    </div>
                                    <div class="mb-3">
                                        <label for="edit-team-points" class="form-label">Total Points</label>
                                        <input type="number" class="form-control" id="edit-team-points" value="${team.total_points || 0}" min="0">
                                    </div>
                                </form>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                                <button type="button" class="btn btn-primary" id="update-team-btn">Update Team</button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            // Add modal to body if it doesn't exist
            if (!document.getElementById('editTeamModal')) {
                document.body.insertAdjacentHTML('beforeend', modalHTML);
            } else {
                document.getElementById('editTeamModal').outerHTML = modalHTML;
            }
            
            // Show modal
            const modal = new bootstrap.Modal(document.getElementById('editTeamModal'));
            modal.show();
            
            // Add event listener to update button
            document.getElementById('update-team-btn').addEventListener('click', handleUpdateTeam);
        })
        .catch(error => {
            console.error('Error fetching team details:', error);
            alert('Error fetching team details. Please try again.');
        });
}

// Handle update team
function handleUpdateTeam() {
    const teamId = document.getElementById('edit-team-id').value;
    const teamName = document.getElementById('edit-team-name').value;
    const captainName = document.getElementById('edit-captain-name').value;
    const contactInfo = document.getElementById('edit-contact-info').value;
    const totalPoints = document.getElementById('edit-team-points').value;
    
    if (!teamName || !captainName || !contactInfo) {
        alert('Please fill in all required fields.');
        return;
    }
    
    fetch(`/api/admin/teams/${teamId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            name: teamName,
            captain_name: captainName,
            contact_info: contactInfo,
            total_points: parseInt(totalPoints)
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert('Error: ' + data.error);
        } else {
            alert('Team updated successfully!');
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('editTeamModal'));
            modal.hide();
            // Reload teams
            loadTeams();
            loadDashboardData();
        }
    })
    .catch(error => {
        console.error('Error updating team:', error);
        alert('An error occurred while updating the team. Please try again.');
    });
}

// Delete team function
function deleteTeam(teamId) {
    if (confirm('Are you sure you want to delete this team? This action cannot be undone.')) {
        fetch(`/api/admin/teams/${teamId}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert('Error: ' + data.error);
            } else {
                alert('Team deleted successfully!');
                // Reload teams
                loadTeams();
                loadDashboardData();
            }
        })
        .catch(error => {
            console.error('Error deleting team:', error);
            alert('An error occurred while deleting the team. Please try again.');
        });
    }
}

// Delete result function
function deleteResult(resultId) {
    if (confirm('Are you sure you want to delete this match result? This action cannot be undone.')) {
        fetch(`/api/admin/results/${resultId}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert('Error: ' + data.error);
            } else {
                alert('Match result deleted successfully!');
                // Reload results
                loadMatchResults();
                // Reload teams to update rankings
                loadTeams();
                loadDashboardData();
            }
        })
        .catch(error => {
            console.error('Error deleting match result:', error);
            alert('An error occurred while deleting the match result. Please try again.');
        });
    }
}
document.getElementById('download-excel-btn').addEventListener('click', function() {
    fetch('/api/teams/export')
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to download Excel file');
            }
            return response.blob();
        })
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'teams.xlsx';
            document.body.appendChild(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(url);
        })
        .catch(error => {
            alert('حدث خطأ أثناء تحميل ملف Excel: ' + error.message);
        });
});
document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('team-search-input');
    const tableBody = document.getElementById('teams-table-body');

    searchInput.addEventListener('input', () => {
        const filter = searchInput.value.toLowerCase();

        // حلق على كل صف في tbody
        Array.from(tableBody.rows).forEach(row => {
            // جمع نصوص الأعمدة المهمة (Name, Captain, Rank) كلها ونحولها لحروف صغيرة
            const name = row.cells[2]?.textContent.toLowerCase() || '';
            const captain = row.cells[3]?.textContent.toLowerCase() || '';
            const rank = row.cells[6]?.textContent.toLowerCase() || '';

            // إذا النص الموجود في البحث موجود في أي عمود من الثلاثة
            if (name.includes(filter) || captain.includes(filter) || rank.includes(filter)) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
    });
});

const teams = [ // مثال ديال الداتا، عوضها بالداتا لي كتجيك من الـ backend
  { id: 1, logo: "logo1.png", name: "Team A", captain: "Player A", registrationDate: "2024-01-01", points: 10, rank: 1 },
  { id: 2, logo: "logo2.png", name: "Team B", captain: "Player B", registrationDate: "2024-01-02", points: 8, rank: 2 }
];

document.addEventListener('DOMContentLoaded', function () {
  var el = document.getElementById('teams-table-body');
  if (el) {
    new Sortable(el, {
      animation: 150,
      ghostClass: 'sortable-ghost',
      onEnd: function(evt) {
        alert('تم تحريك الصف من ' + (evt.oldIndex + 1) + ' إلى ' + (evt.newIndex + 1));
      }
    });
  }
})
