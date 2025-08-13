module.exports = function(eleventyConfig) {
  // Copy static assets (CSS & JS) directly to output
  eleventyConfig.addPassthroughCopy("src/styles.css");
  eleventyConfig.addPassthroughCopy("src/script.js");

  return {
    dir: {
      input: "src",
      output: "_site"
    }
  };
};
