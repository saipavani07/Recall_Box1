"use strict";

// ======================================
// 1. OPEN RECALLBOX
// ======================================

function openRecallBox() {
    const landingPage = document.getElementById("landingPage");
    const mainApplication = document.getElementById("mainApplication");

    if (landingPage) {
        landingPage.style.display = "none";
    }

    if (mainApplication) {
        mainApplication.style.display = "block";
    }

    window.scrollTo(0, 0);
}


// ======================================
// 2. SHOW / HIDE MEMORY DETAILS
// ======================================

function toggleMemoryDetails(button) {
    const card = button.closest(".memory-card");

    if (!card) return;

    const details = card.querySelector(".memory-details");

    if (!details) return;

    const isHidden =
        details.style.display === "none" ||
        getComputedStyle(details).display === "none";

    details.style.display = isHidden ? "block" : "none";

    button.textContent = isHidden
        ? "Hide Details ↑"
        : "View Details ↓";
}


// ======================================
// 3. SHOW / HIDE EDIT FORM
// ======================================

function toggleEditForm(button) {
    const card = button.closest(".memory-card");

    if (!card) return;

    const editForm = card.querySelector(".edit-form");

    if (!editForm) return;

    editForm.hidden = !editForm.hidden;

    button.textContent = editForm.hidden
        ? "✏️ Edit Memory"
        : "Close Edit Form";
}


// ======================================
// 4. SEARCH AND CATEGORY FILTER
// ======================================

function filterMemories() {
    const searchInput = document.getElementById("searchInput");
    const categoryFilter = document.getElementById("categoryFilter");

    if (!searchInput || !categoryFilter) return;

    const searchText = searchInput.value.toLowerCase().trim();
    const selectedCategory = categoryFilter.value;

    const cards = document.querySelectorAll(".memory-card");

    cards.forEach(function(card) {
        const title =
            card.querySelector(".memory-title")?.textContent.toLowerCase() || "";

        const content =
            card.querySelector(".memory-content")?.textContent.toLowerCase() || "";

        const category = card.dataset.category || "";

        const matchesSearch =
            title.includes(searchText) ||
            content.includes(searchText);

        const matchesCategory =
            selectedCategory === "all" ||
            category === selectedCategory;

        card.style.display =
            matchesSearch && matchesCategory ? "" : "none";
    });
}


// ======================================
// 5. SORT MEMORIES
// ======================================

function sortMemories() {
    const memoryList = document.getElementById("memoryList");
    const sortSelect = document.getElementById("sortSelect");

    if (!memoryList || !sortSelect) return;

    const cards = Array.from(
        memoryList.querySelectorAll(".memory-card")
    );

    const sortValue = sortSelect.value;

    cards.sort(function(a, b) {

        const titleA = a.dataset.title ||
            a.querySelector(".memory-title")?.textContent.toLowerCase() || "";

        const titleB = b.dataset.title ||
            b.querySelector(".memory-title")?.textContent.toLowerCase() || "";

        const dateA = a.dataset.date || "";
        const dateB = b.dataset.date || "";

        switch (sortValue) {

            case "oldest":
                return dateA.localeCompare(dateB);

            case "az":
                return titleA.localeCompare(titleB);

            case "za":
                return titleB.localeCompare(titleA);

            case "newest":
            default:
                return dateB.localeCompare(dateA);
        }
    });

    cards.forEach(function(card) {
        memoryList.appendChild(card);
    });
}


// ======================================
// 6. SET MINIMUM REMINDER DATE
// ======================================

document.addEventListener("DOMContentLoaded", function() {

    const reminderDate = document.getElementById("reminderDate");

    if (reminderDate) {
        const today = new Date();

        const year = today.getFullYear();
        const month = String(today.getMonth() + 1).padStart(2, "0");
        const day = String(today.getDate()).padStart(2, "0");

        reminderDate.min = `${year}-${month}-${day}`;
    }

});


// ======================================
// 7. CONFIRM MEMORY DELETION
// ======================================

function confirmDelete() {
    return confirm("Are you sure you want to delete this memory?");
}


// ======================================
// 8. PREVENT EMPTY MEMORY FORM
// ======================================

document.addEventListener("DOMContentLoaded", function() {

    const memoryForm = document.getElementById("memoryForm");

    if (memoryForm) {

        memoryForm.addEventListener("submit", function(event) {

            const title = document.getElementById("title").value.trim();
            const content = document.getElementById("content").value.trim();

            if (!title || !content) {
                event.preventDefault();
                alert("Please enter both the title and memory details.");
            }

        });

    }

});


// ======================================
// 9. PREVENT EMPTY REMINDER FORM
// ======================================

document.addEventListener("DOMContentLoaded", function() {

    const reminderForm = document.querySelector(".modern-reminder-form");

    if (reminderForm) {

        reminderForm.addEventListener("submit", function(event) {

            const title = document.getElementById("reminderTitle").value.trim();
            const date = document.getElementById("reminderDate").value;
            const time = document.getElementById("reminderTime").value;

            if (!title || !date || !time) {
                event.preventDefault();
                alert("Please fill in all reminder details.");
            }

        });

    }

});


// ======================================
// 10. AUTO HIDE FLASH MESSAGES
// ======================================

document.addEventListener("DOMContentLoaded", function() {

    const messages = document.querySelectorAll(".flash-message");

    messages.forEach(function(message) {

        setTimeout(function() {

            message.style.transition = "opacity 0.5s ease";
            message.style.opacity = "0";

            setTimeout(function() {
                message.remove();
            }, 500);

        }, 4000);

    });

});


// ======================================
// 11. CLEAR SEARCH AND FILTER
// ======================================

function resetMemoryFilters() {

    const searchInput = document.getElementById("searchInput");
    const categoryFilter = document.getElementById("categoryFilter");
    const sortSelect = document.getElementById("sortSelect");

    if (searchInput) searchInput.value = "";

    if (categoryFilter) categoryFilter.value = "all";

    if (sortSelect) sortSelect.value = "newest";

    filterMemories();
    sortMemories();
}


// ======================================
// RECALLBOX JAVASCRIPT READY
// ======================================

console.log("RecallBox JavaScript loaded successfully!");
