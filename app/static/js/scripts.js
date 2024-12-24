/*!
* Start Bootstrap - Personal v1.0.1 (https://startbootstrap.com/template-overviews/personal)
* Copyright 2013-2023 Start Bootstrap
* Licensed under MIT (https://github.com/StartBootstrap/startbootstrap-personal/blob/master/LICENSE)
*/
// This file is intentionally blank
// Use this file to add JavaScript to your project
document.addEventListener("DOMContentLoaded", () => {
    const imageContainers = document.querySelectorAll(".image-container");

    imageContainers.forEach(imageContainer => {
        const img = imageContainer.querySelector(".zoom-pan-effect");

        imageContainer.addEventListener("mousemove", (e) => {
            const rect = imageContainer.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            const xPercent = (x / rect.width) * 100;
            const yPercent = (y / rect.height) * 100;

            img.style.transformOrigin = `${xPercent}% ${yPercent}%`;
        }, 16);
    });
});
