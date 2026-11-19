import React from 'react';
import {Composition} from 'remotion';
import {Test} from './Test';
import {TheDopAd, DURATION} from './TheDopAd';
export const Root: React.FC = () => (
  <>
    <Composition id="Test" component={Test} durationInFrames={60} fps={30} width={1080} height={1920} />
    <Composition id="TheDopAd" component={TheDopAd} durationInFrames={DURATION} fps={30} width={1080} height={1920} />
  </>
);
