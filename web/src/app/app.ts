import { Component, signal, ChangeDetectionStrategy, inject } from '@angular/core';
import { TopBanner } from './top-banner/top-banner';
import { RouterOutlet } from '@angular/router';
import { ChatbotDrawerComponent } from './schedule-page/chatbot-drawer/chatbot-drawer';
import { ChatbotService } from './services/chatbot-service/chatbot-service';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, TopBanner, ChatbotDrawerComponent],
  templateUrl: './app.html',
  styleUrl: './app.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
  host: {
    class: 'block w-full h-full'
  }
})
export class App {
  chatbotService = inject(ChatbotService);
  protected readonly title = signal('web');
}
