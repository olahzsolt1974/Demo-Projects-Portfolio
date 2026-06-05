const filters = document.querySelectorAll(".filter");
const cards = document.querySelectorAll(".project-card");

filters.forEach((filter) => {
  filter.addEventListener("click", () => {
    const category = filter.dataset.filter;

    filters.forEach((item) => item.classList.remove("active"));
    filter.classList.add("active");

    cards.forEach((card) => {
      const categories = card.dataset.category.split(" ");
      const shouldShow = category === "all" || categories.includes(category);
      card.classList.toggle("is-hidden", !shouldShow);
    });
  });
});
