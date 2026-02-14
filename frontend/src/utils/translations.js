/**
 * Translation utilities for multi-language support
 */

const translations = {
  en: {
    true: 'True',
    false: 'False'
  },
  ar: {
    true: 'صحيح',
    false: 'خاطئ'
  }
};

/**
 * Get translated True/False label based on language
 * @param {boolean|string} value - The boolean value or string 'True'/'False'
 * @param {string} language - ISO 639-1 language code (e.g., 'en', 'ar')
 * @returns {string} Translated label
 */
export function getTrueFalseLabel(value, language = 'en') {
  const lang = translations[language] || translations.en;
  const isTrue = value === true || value === 'True' || value === 'true';
  return isTrue ? lang.true : lang.false;
}

/**
 * Get True/False options array for rendering
 * @param {string} language - ISO 639-1 language code
 * @returns {Array<{value: string, label: string}>} Array of option objects
 */
export function getTrueFalseOptions(language = 'en') {
  const lang = translations[language] || translations.en;
  return [
    { value: 'True', label: lang.true },
    { value: 'False', label: lang.false }
  ];
}
