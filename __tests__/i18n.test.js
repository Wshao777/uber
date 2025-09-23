import i18n from '../i18n';

test('loads Chinese translations', () => {
  i18n.changeLanguage('zh');
  expect(i18n.t('welcome.skip')).toBe('跳过');
});
