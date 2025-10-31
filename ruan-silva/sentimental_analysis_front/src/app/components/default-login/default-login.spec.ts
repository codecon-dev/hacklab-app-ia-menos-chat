import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DefaultLogin } from './default-login';

describe('DefaultLogin', () => {
  let component: DefaultLogin;
  let fixture: ComponentFixture<DefaultLogin>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DefaultLogin]
    })
    .compileComponents();

    fixture = TestBed.createComponent(DefaultLogin);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
