import { ContentModel } from './content.model';
import { Image } from './image.model';

export class CardModel {
  constructor(
    public image?: Image,
    public content?: ContentModel
  ) {}
}
