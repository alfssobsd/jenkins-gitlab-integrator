import { AngularAdminUiPage } from './app.po';

describe('angular-admin-ui App', () => {
  let page: AngularAdminUiPage;

  beforeEach(() => {
    page = new AngularAdminUiPage();
  });

  it('should display welcome message', () => {
    page.navigateTo();
    expect(page.getParagraphText()).toEqual('Welcome to app!');
  });
});
