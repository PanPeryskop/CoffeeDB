document.addEventListener("DOMContentLoaded", function () {
  initNotifications();

  initPasswordToggle();

  initScrollAnimations();
});

function initNotifications() {
  const notifications = document.querySelectorAll(".notification");

  notifications.forEach((notification) => {
    const closeBtn = notification.querySelector(".close-btn");

    if (closeBtn) {
      closeBtn.addEventListener("click", () => {
        notification.style.animation = "fadeOut 0.5s forwards";
        setTimeout(() => {
          notification.remove();
        }, 500);
      });
    }

    setTimeout(() => {
      if (notification.parentElement) {
        notification.style.animation = "fadeOut 0.5s forwards";
        setTimeout(() => {
          if (notification.parentElement) {
            notification.remove();
          }
        }, 500);
      }
    }, 5000);
  });
}

function initPasswordToggle() {
  const toggleBtns = document.querySelectorAll(".toggle-password");

  toggleBtns.forEach((btn) => {
    btn.addEventListener("click", function () {
      const input = this.previousElementSibling;
      const icon = this.querySelector("i");

      if (input.type === "password") {
        input.type = "text";
        icon.className = "fas fa-eye-slash";
      } else {
        input.type = "password";
        icon.className = "fas fa-eye";
      }
    });
  });
}

function initScrollAnimations() {
  const animatedElements = document.querySelectorAll(
    ".feature-card, .coffee-card"
  );

  checkElementsInView();

  window.addEventListener("scroll", checkElementsInView);

  function checkElementsInView() {
    animatedElements.forEach((element) => {
      const elementPosition = element.getBoundingClientRect();
      const windowHeight = window.innerHeight;

      if (elementPosition.top < windowHeight * 0.85) {
        element.classList.add("animate");
      }
    });
  }
}

document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
  anchor.addEventListener("click", function (e) {
    e.preventDefault();

    const targetId = this.getAttribute("href");
    if (targetId === "#") return;

    const targetElement = document.querySelector(targetId);
    if (targetElement) {
      targetElement.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    }
  });
});

const currentPath = window.location.pathname;
const navLinks = document.querySelectorAll(".nav-link");

navLinks.forEach((link) => {
  const linkPath = link.getAttribute("href");
  if (
    currentPath === linkPath ||
    (currentPath.startsWith(linkPath) && linkPath !== "/")
  ) {
    link.classList.add("active");
  }
});

const forms = document.querySelectorAll("form");

forms.forEach((form) => {
  form.addEventListener("submit", function (e) {
    let isValid = true;

    const requiredInputs = form.querySelectorAll("[required]");
    requiredInputs.forEach((input) => {
      if (!input.value.trim()) {
        isValid = false;
        highlightInput(input, true);
      } else {
        highlightInput(input, false);
      }
    });

    const emailInputs = form.querySelectorAll('input[type="email"]');
    emailInputs.forEach((input) => {
      if (input.value && !isValidEmail(input.value)) {
        isValid = false;
        highlightInput(input, true);
      }
    });

    if (!isValid) {
      e.preventDefault();
    }
  });
});

function highlightInput(input, isError) {
  if (isError) {
    input.classList.add("error");
    const errorMsg = document.createElement("div");
    errorMsg.className = "error-message";
    errorMsg.textContent = "To pole jest wymagane";

    if (
      input.nextElementSibling &&
      input.nextElementSibling.classList.contains("error-message")
    ) {
      input.parentNode.removeChild(input.nextElementSibling);
    }

    input.parentNode.insertBefore(errorMsg, input.nextElementSibling);
  } else {
    input.classList.remove("error");
    if (
      input.nextElementSibling &&
      input.nextElementSibling.classList.contains("error-message")
    ) {
      input.parentNode.removeChild(input.nextElementSibling);
    }
  }
}

function isValidEmail(email) {
  const re =
    /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
  return re.test(String(email).toLowerCase());
}

const buttons = document.querySelectorAll(".btn");

buttons.forEach((button) => {
  button.addEventListener("click", function (e) {
    const ripple = document.createElement("span");
    ripple.classList.add("ripple");

    const rect = button.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);

    ripple.style.width = ripple.style.height = `${size}px`;
    ripple.style.left = `${e.clientX - rect.left - size / 2}px`;
    ripple.style.top = `${e.clientY - rect.top - size / 2}px`;

    button.appendChild(ripple);

    setTimeout(() => {
      ripple.remove();
    }, 600);
  });
});
