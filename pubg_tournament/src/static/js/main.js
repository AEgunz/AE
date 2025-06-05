// Main JavaScript for PUBG Mobile Tournament Website

document.addEventListener('DOMContentLoaded', function() {
    fetchSiteConfig();
    fetchUpcomingMatches();
    fetchLiveMatches();
    fetchTeams();
    fetchRankings();

    const registrationForm = document.getElementById('team-registration-form');
    if (registrationForm) {
        registrationForm.addEventListener('submit', handleTeamRegistration);
    }
});

// Fetch site configuration
function fetchSiteConfig() {
    fetch('/api/config/')
        .then(response => response.json())
        .then(data => {
            // Set donation link
            const donationLinks = document.querySelectorAll('#donation-link, #donation-footer-link');
            donationLinks.forEach(link => {
                link.href = data.donation_link || 'https://streamlabs.com/aegaming91/tip';
            });
            
            // Set YouTube channel link
            const youtubeLinks = document.querySelectorAll('#youtube-link, #youtube-footer-link');
            youtubeLinks.forEach(link => {
                link.href = data.youtube_channel || 'https://www.youtube.com/@Aegaming91';
            });
            
            // Set site title if needed
            if (data.site_title) {
                document.title = data.site_title;
                const tournamentTitle = document.querySelector('.tournament-title');
                if (tournamentTitle) {
                    tournamentTitle.textContent = data.site_title;
                }
            }
        })
        .catch(error => {
            console.error('Error fetching site config:', error);
        });
}

// Fetch upcoming matches
function fetchUpcomingMatches() {
    fetch('/api/matches/upcoming')
        .then(response => response.json())
        .then(matches => {
            const upcomingMatchesList = document.getElementById('upcoming-matches-list');
            if (upcomingMatchesList) {
                if (matches.length === 0) {
                    upcomingMatchesList.innerHTML = '<p>No upcoming matches scheduled</p>';
                } else {
                    let html = '<ul class="upcoming-matches-list">';
                    matches.forEach(match => {
                        const matchDate = new Date(match.match_date);
                        html += `
                            <li class="upcoming-match-item">
                                <div class="match-name">${match.name}</div>
                                <div class="match-details">
                                    <span class="match-date">${formatDate(matchDate)}</span>
                                    <span class="match-map">${match.map_name}</span>
                                </div>
                            </li>
                        `;
                    });
                    html += '</ul>';
                    upcomingMatchesList.innerHTML = html;
                }
            }
            
            // Also update the schedule section
            updateMatchSchedule(matches);
        })
        .catch(error => {
            console.error('Error fetching upcoming matches:', error);
            const upcomingMatchesList = document.getElementById('upcoming-matches-list');
            if (upcomingMatchesList) {
                upcomingMatchesList.innerHTML = '<p>Error loading upcoming matches</p>';
            }
        });
}

// Fetch live matches
function fetchLiveMatches() {
    fetch('/api/matches/live')
        .then(response => response.json())
        .then(matches => {
            const currentMatch = document.getElementById('current-match');
            if (currentMatch) {
                if (matches.length === 0) {
                    currentMatch.innerHTML = '<p>No matches currently live</p>';
                } else {
                    const match = matches[0]; // Display the first live match
                    const matchDate = new Date(match.match_date);
                    let html = `
                        <div class="live-match-info">
                            <h4 class="match-name">${match.name}</h4>
                            <div class="match-details">
                                <p><strong>Date:</strong> ${formatDate(matchDate)}</p>
                                <p><strong>Map:</strong> ${match.map_name}</p>
                            </div>
                            <div class="watch-container">
                                <a href="${match.youtube_link || 'https://www.youtube.com/@Aegaming91'}" 
                                   class="btn btn-danger" target="_blank">
                                   Watch Now
                                </a>
                            </div>
                        </div>
                    `;
                    currentMatch.innerHTML = html;
                }
            }
        })
        .catch(error => {
            console.error('Error fetching live matches:', error);
            const currentMatch = document.getElementById('current-match');
            if (currentMatch) {
                currentMatch.innerHTML = '<p>Error loading live match information</p>';
            }
        });
}

// Update match schedule section
function updateMatchSchedule(matches) {
    const matchSchedule = document.getElementById('match-schedule');
    if (matchSchedule) {
        if (!matches || matches.length === 0) {
            matchSchedule.innerHTML = '<p class="text-center">No matches scheduled at this time</p>';
        } else {
            let html = '<div class="schedule-list">';
            matches.forEach(match => {
                const matchDate = new Date(match.match_date);
                html += `
                    <div class="schedule-item">
                        <div class="schedule-date">
                            <div class="date">${matchDate.getDate()}</div>
                            <div class="month">${matchDate.toLocaleString('default', { month: 'short' })}</div>
                        </div>
                        <div class="schedule-details">
                            <h4 class="match-name">${match.name}</h4>
                            <div class="match-info">
                                <span class="match-time">${matchDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                                <span class="match-map">${match.map_name}</span>
                                <span class="match-status ${match.status}">${match.status}</span>
                            </div>
                        </div>
                    </div>
                `;
            });
            html += '</div>';
            matchSchedule.innerHTML = html;
        }
    }
}

// Fetch all teams
function fetchTeams() {
    fetch('/api/teams/')
        .then(response => response.json())
        .then(teams => {
            const teamsContainer = document.getElementById('teams-container');
            if (teamsContainer) {
                if (teams.length === 0) {
                    teamsContainer.innerHTML = '<p class="text-center">No teams registered yet</p>';
                } else {
                    let html = '';
                    teams.forEach(team => {
                        html += `
                            <div class="team-card">
                                <div class="team-logo-container">
                                    <img src="${team.logo_path}" alt="${team.name} Logo" class="team-logo">
                                </div>
                                <div class="team-info">
                                    <h3 class="team-name">${team.name}</h3>
                                    <p class="team-captain">Captain: ${team.captain_name}</p>
                                    <p class="team-rank">Rank: ${team.rank || 'N/A'}</p>
                                    <p class="team-points">Points: ${team.total_points || '0'}</p>
                                </div>
                            </div>
                        `;
                    });
                    teamsContainer.innerHTML = html;
                }
            }
        })
        .catch(error => {
            console.error('Error fetching teams:', error);
            const teamsContainer = document.getElementById('teams-container');
            if (teamsContainer) {
                teamsContainer.innerHTML = '<p class="text-center">Error loading teams</p>';
            }
        });
}


// Handle team registration form submission
function handleTeamRegistration(event) {
    event.preventDefault();
    
    const form = event.target;
    const formData = new FormData(form);
    
    // Show loading state
    const submitButton = form.querySelector('button[type="submit"]');
    const originalButtonText = submitButton.textContent;
    submitButton.textContent = 'Registering...';
    submitButton.disabled = true;
    
    fetch('/api/teams/register', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert('Error: ' + data.error);
        } else {
            alert('Team registered successfully!');
            form.reset();
            // Refresh teams list
            fetchTeams();
        }
    })
    .catch(error => {
        console.error('Error registering team:', error);
        alert('An error occurred while registering your team. Please try again.');
    })
    .finally(() => {
        // Reset button state
        submitButton.textContent = originalButtonText;
        submitButton.disabled = false;
    });
}

// Helper function to format dates
function formatDate(date) {
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

const btn = document.getElementById("scrollTopBtn");

window.onscroll = function () {
  if (document.body.scrollTop > 300 || document.documentElement.scrollTop > 300) {
    btn.style.display = "block";
  } else {
    btn.style.display = "none";
  }
};

function scrollToTop() {
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

const menuBtn = document.querySelector('.menu-button');

if (menuBtn) {  // نتأكد أن العنصر كاين
  menuBtn.addEventListener('click', () => {
    const expanded = menuBtn.getAttribute('aria-expanded') === 'true' || false;
    menuBtn.setAttribute('aria-expanded', !expanded);
    // هنا تقدر تضيف كود لفتح وإغلاق القائمة (مثلاً toggle collapse)
  });
}



// Check registration status and update buttons
function checkRegistrationStatus() {
    const heroRegisterButton = document.getElementById('hero-register-button');
    const formRegisterButton = document.querySelector('#team-registration-form button[type="submit"]');
    const registrationSectionTitle = document.querySelector('#register h2'); // Get the title of the registration section

    fetch('/api/register/can_register')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'closed') {
                if (heroRegisterButton) {
                    heroRegisterButton.textContent = data.message || 'Registration Closed';
                    heroRegisterButton.classList.remove('btn-primary', 'btn-pulse');
                    heroRegisterButton.classList.add('btn-secondary', 'disabled');
                    heroRegisterButton.style.pointerEvents = 'none'; // Make it unclickable
                    heroRegisterButton.href = '#'; // Prevent scrolling
                }
                if (formRegisterButton) {
                    formRegisterButton.textContent = data.message || 'Registration Closed';
                    formRegisterButton.disabled = true;
                    formRegisterButton.classList.remove('btn-primary');
                    formRegisterButton.classList.add('btn-secondary');
                }
                // Optionally, update the section title or add a message
                if (registrationSectionTitle) {
                    const statusMessage = document.createElement('p');
                    statusMessage.textContent = data.message || 'Registration is currently closed.';
                    statusMessage.style.color = 'red';
                    statusMessage.style.textAlign = 'center';
                    registrationSectionTitle.parentNode.insertBefore(statusMessage, registrationSectionTitle.nextSibling);
                }

            } else if (data.status === 'open') {
                 if (heroRegisterButton) {
                    heroRegisterButton.textContent = 'Register Your Team ✍️';
                    heroRegisterButton.classList.remove('btn-secondary', 'disabled');
                    heroRegisterButton.classList.add('btn-primary', 'btn-pulse');
                    heroRegisterButton.style.pointerEvents = 'auto';
                    heroRegisterButton.href = '#register';
                }
                if (formRegisterButton) {
                    formRegisterButton.textContent = 'Register Team';
                    formRegisterButton.disabled = false;
                    formRegisterButton.classList.remove('btn-secondary');
                    formRegisterButton.classList.add('btn-primary');
                }
                 // Optionally display open status
                if (registrationSectionTitle && data.message) {
                    const statusMessage = document.createElement('p');
                    statusMessage.textContent = data.message;
                    statusMessage.style.color = 'green';
                    statusMessage.style.textAlign = 'center';
                    registrationSectionTitle.parentNode.insertBefore(statusMessage, registrationSectionTitle.nextSibling);
                }
            } else {
                 // Handle potential errors or unexpected statuses
                 console.warn('Unexpected registration status:', data.status, data.message);
            }
        })
        .catch(error => {
            console.error('Error fetching registration status:', error);
            // Optionally inform the user about the error
            if (registrationSectionTitle) {
                 const errorMessage = document.createElement('p');
                 errorMessage.textContent = 'Could not check registration status. Please try again later.';
                 errorMessage.style.color = 'orange';
                 errorMessage.style.textAlign = 'center';
                 registrationSectionTitle.parentNode.insertBefore(errorMessage, registrationSectionTitle.nextSibling);
            }
        });
}


// Modify the DOMContentLoaded listener to call the new function
document.addEventListener('DOMContentLoaded', function() {
    // Fetch site configuration (including donation and YouTube links)
    fetchSiteConfig();
    
    // Check registration status FIRST
    checkRegistrationStatus();

    // Fetch upcoming matches
    fetchUpcomingMatches();
    
    // Fetch live matches
    fetchLiveMatches();
    
    // Fetch all teams
    fetchTeams();
    
    // Fetch rankings
    
function fetchRankings() {
    fetch('/api/rankings')
        .then(response => response.json())
        .then(data => {
            const rankingsContainer = document.getElementById('rankings-container');
            if (rankingsContainer) {
                if (data.length === 0) {
                    rankingsContainer.innerHTML = '<p>No rankings available</p>';
                } else {
                    let html = '<ul>';
                    data.forEach((item, index) => {
                        html += `<li>${index + 1}. ${item.team_name} - ${item.points} pts</li>`;
                    });
                    html += '</ul>';
                    rankingsContainer.innerHTML = html;
                }
            }
        })
        .catch(error => {
            console.error('Error fetching rankings:', error);
            const rankingsContainer = document.getElementById('rankings-container');
            if (rankingsContainer) {
                rankingsContainer.innerHTML = '<p>Error loading rankings</p>';
            }
        });
}
    
    // Handle team registration form submission
    const registrationForm = document.getElementById('team-registration-form');
    if (registrationForm) {
        registrationForm.addEventListener('submit', handleTeamRegistration);
    }
});

