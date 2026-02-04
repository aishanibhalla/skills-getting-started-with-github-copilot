document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;

        // Participants section
        let participantsSection = document.createElement("div");
        participantsSection.className = "participants-section";
        const strong = document.createElement("strong");
        strong.textContent = "Participants:";
        participantsSection.appendChild(strong);

        if (details.participants.length > 0) {
          const ul = document.createElement("ul");
          ul.style.listStyleType = "none";
          ul.style.paddingLeft = "0";
          details.participants.forEach(email => {
            const li = document.createElement("li");
            li.style.display = "flex";
            li.style.alignItems = "center";
            // Email span
            const span = document.createElement("span");
            span.textContent = email;
            // Delete button
            const deleteBtn = document.createElement("button");
            deleteBtn.innerHTML = "🗑️";
            deleteBtn.title = "Unregister";
            deleteBtn.style.marginLeft = "8px";
            deleteBtn.style.background = "none";
            deleteBtn.style.border = "none";
            deleteBtn.style.cursor = "pointer";
            deleteBtn.onclick = async function() {
              await unregisterParticipant(name, email);
            };
            li.appendChild(span);
            li.appendChild(deleteBtn);
            ul.appendChild(li);
          });
          participantsSection.appendChild(ul);
        } else {
          const noPart = document.createElement("span");
          noPart.className = "no-participants";
          noPart.textContent = "No participants yet";
          participantsSection.appendChild(noPart);
        }

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
        `;
        activityCard.appendChild(participantsSection);

        activitiesList.appendChild(activityCard);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
        fetchActivities(); // Refresh activities list after successful signup
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Unregister participant function
  async function unregisterParticipant(activity, email) {
    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/unregister`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({ email })
        }
      );
      if (response.ok) {
        fetchActivities();
      } else {
        alert("Failed to unregister participant.");
      }
    } catch (error) {
      alert("Error unregistering participant.");
    }
  }

  // Initialize app
  fetchActivities();
});
