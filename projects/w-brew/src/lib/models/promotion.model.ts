export class Promotion {
  constructor(
    public heading?: string,
    public subHeading?: string,
    public isForm?: boolean,
    public formPrimaryButton?: string,
    public formSecondaryButton?: string,
    public backgroundImageUrl?: string,
    public controlConfiguration?: {[key: string]: string},
    public controlConfigurationValues?: {[key: string]: string},
    public isRegistered?: boolean
  ) {}
}
