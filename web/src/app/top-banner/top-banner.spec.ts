import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TopBanner } from './top-banner';

describe('TopBanner', () => {
  let component: TopBanner;
  let fixture: ComponentFixture<TopBanner>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TopBanner]
    })
    .compileComponents();

    fixture = TestBed.createComponent(TopBanner);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
