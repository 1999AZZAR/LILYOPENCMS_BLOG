/*
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
*/

// Brand Management JavaScript
let COLOR_VARIABLES = [];

// Professional Color Palettes
const FIXED_PRESETS = {
  'Current': {
    '--background': '51 100% 95% / 1',
    '--foreground': '220 80% 20% / 1',
    '--card': '0 0% 100% / 1',
    '--card-foreground': '220 80% 20% / 1',
    '--popover': '0 0% 100% / 1',
    '--popover-foreground': '220 80% 20% / 1',
    '--primary': '200 100% 50% / 1',
    '--primary-foreground': '0 0% 100% / 1',
    '--secondary': '340 100% 70% / 1',
    '--secondary-foreground': '220 80% 20% / 1',
    '--muted': '120 60% 90% / 1',
    '--muted-foreground': '220 80% 20% / 1',
    '--accent': '40 100% 60% / 1',
    '--accent-foreground': '220 80% 20% / 1',
    '--destructive': '0 72% 51% / 1',
    '--destructive-foreground': '0 0% 100% / 1',
    '--border': '220 13% 91% / 1',
    '--input': '0 0% 100% / 1',
    '--ring': '200 100% 50% / 1'
  },
  'Original': {
    '--background': '220 20% 99% / 1',
    '--foreground': '220 10% 15% / 1',
    '--card': '0 0% 100% / 1',
    '--card-foreground': '220 10% 15% / 1',
    '--popover': '0 0% 100% / 1',
    '--popover-foreground': '220 10% 15% / 1',
    '--primary': '358 50% 39% / 1',
    '--primary-foreground': '0 0% 100% / 1',
    '--secondary': '220 14% 96% / 1',
    '--secondary-foreground': '220 9% 31% / 1',
    '--muted': '220 14% 96% / 1',
    '--muted-foreground': '220 9% 46% / 1',
    '--accent': '220 14% 96% / 1',
    '--accent-foreground': '220 10% 15% / 1',
    '--destructive': '0 72% 51% / 1',
    '--destructive-foreground': '0 0% 100% / 1',
    '--border': '220 13% 91% / 1',
    '--input': '0 0% 100% / 1',
    '--ring': '358 50% 39% / 1'
  },
  'Light': {
    '--background': '0 0% 100% / 1',
    '--foreground': '222 84% 4.9% / 1',
    '--card': '0 0% 100% / 1',
    '--card-foreground': '222 84% 4.9% / 1',
    '--popover': '0 0% 100% / 1',
    '--popover-foreground': '222 84% 4.9% / 1',
    '--primary': '222 84% 4.9% / 1',
    '--primary-foreground': '210 40% 98% / 1',
    '--secondary': '210 40% 96% / 1',
    '--secondary-foreground': '222 84% 4.9% / 1',
    '--muted': '210 40% 96% / 1',
    '--muted-foreground': '215 16% 47% / 1',
    '--accent': '210 40% 96% / 1',
    '--accent-foreground': '222 84% 4.9% / 1',
    '--destructive': '0 84% 60% / 1',
    '--destructive-foreground': '210 40% 98% / 1',
    '--border': '214 32% 91% / 1',
    '--input': '214 32% 91% / 1',
    '--ring': '222 84% 4.9% / 1'
  },
  'Dark': {
    '--background': '222 84% 4.9% / 1',
    '--foreground': '210 40% 98% / 1',
    '--card': '222 84% 4.9% / 1',
    '--card-foreground': '210 40% 98% / 1',
    '--popover': '222 84% 4.9% / 1',
    '--popover-foreground': '210 40% 98% / 1',
    '--primary': '210 40% 98% / 1',
    '--primary-foreground': '222 84% 4.9% / 1',
    '--secondary': '217 33% 17% / 1',
    '--secondary-foreground': '210 40% 98% / 1',
    '--muted': '217 33% 17% / 1',
    '--muted-foreground': '215 20% 65% / 1',
    '--accent': '217 33% 17% / 1',
    '--accent-foreground': '210 40% 98% / 1',
    '--destructive': '0 63% 31% / 1',
    '--destructive-foreground': '210 40% 98% / 1',
    '--border': '217 33% 17% / 1',
    '--input': '217 33% 17% / 1',
    '--ring': '212 100% 50% / 1'
  },
  'Capuchin': {
    '--background': '45 100% 98% / 1',
    '--foreground': '25 30% 15% / 1',
    '--card': '45 100% 99% / 1',
    '--card-foreground': '25 30% 15% / 1',
    '--popover': '45 100% 99% / 1',
    '--popover-foreground': '25 30% 15% / 1',
    '--primary': '25 95% 53% / 1',
    '--primary-foreground': '45 100% 98% / 1',
    '--secondary': '35 100% 85% / 1',
    '--secondary-foreground': '25 30% 15% / 1',
    '--muted': '45 50% 92% / 1',
    '--muted-foreground': '25 30% 35% / 1',
    '--accent': '15 100% 70% / 1',
    '--accent-foreground': '25 30% 15% / 1',
    '--destructive': '0 84% 60% / 1',
    '--destructive-foreground': '45 100% 98% / 1',
    '--border': '45 50% 88% / 1',
    '--input': '45 100% 99% / 1',
    '--ring': '25 95% 53% / 1'
  },
  'Golden Orange': {
    '--background': '35 100% 97% / 1',
    '--foreground': '35 40% 15% / 1',
    '--card': '35 100% 99% / 1',
    '--card-foreground': '35 40% 15% / 1',
    '--popover': '35 100% 99% / 1',
    '--popover-foreground': '35 40% 15% / 1',
    '--primary': '35 100% 50% / 1',
    '--primary-foreground': '35 100% 97% / 1',
    '--secondary': '25 100% 80% / 1',
    '--secondary-foreground': '35 40% 15% / 1',
    '--muted': '35 50% 90% / 1',
    '--muted-foreground': '35 40% 35% / 1',
    '--accent': '45 100% 65% / 1',
    '--accent-foreground': '35 40% 15% / 1',
    '--destructive': '0 84% 60% / 1',
    '--destructive-foreground': '35 100% 97% / 1',
    '--border': '35 50% 85% / 1',
    '--input': '35 100% 99% / 1',
    '--ring': '35 100% 50% / 1'
  },
  'Ocean': {
    '--background': '190 50% 98% / 1',
    '--foreground': '190 40% 15% / 1',
    '--card': '190 50% 99% / 1',
    '--card-foreground': '190 40% 15% / 1',
    '--popover': '190 50% 99% / 1',
    '--popover-foreground': '190 40% 15% / 1',
    '--primary': '190 100% 45% / 1',
    '--primary-foreground': '190 50% 98% / 1',
    '--secondary': '180 100% 80% / 1',
    '--secondary-foreground': '190 40% 15% / 1',
    '--muted': '190 30% 90% / 1',
    '--muted-foreground': '190 40% 35% / 1',
    '--accent': '170 100% 70% / 1',
    '--accent-foreground': '190 40% 15% / 1',
    '--destructive': '0 84% 60% / 1',
    '--destructive-foreground': '190 50% 98% / 1',
    '--border': '190 30% 85% / 1',
    '--input': '190 50% 99% / 1',
    '--ring': '190 100% 45% / 1'
  },
  'Forest': {
    '--background': '140 30% 98% / 1',
    '--foreground': '140 40% 15% / 1',
    '--card': '140 30% 99% / 1',
    '--card-foreground': '140 40% 15% / 1',
    '--popover': '140 30% 99% / 1',
    '--popover-foreground': '140 40% 15% / 1',
    '--primary': '140 100% 35% / 1',
    '--primary-foreground': '140 30% 98% / 1',
    '--secondary': '160 100% 80% / 1',
    '--secondary-foreground': '140 40% 15% / 1',
    '--muted': '140 20% 90% / 1',
    '--muted-foreground': '140 40% 35% / 1',
    '--accent': '120 100% 70% / 1',
    '--accent-foreground': '140 40% 15% / 1',
    '--destructive': '0 84% 60% / 1',
    '--destructive-foreground': '140 30% 98% / 1',
    '--border': '140 20% 85% / 1',
    '--input': '140 30% 99% / 1',
    '--ring': '140 100% 35% / 1'
  },
  'Sunset': {
    '--background': '10 100% 98% / 1',
    '--foreground': '10 40% 15% / 1',
    '--card': '10 100% 99% / 1',
    '--card-foreground': '10 40% 15% / 1',
    '--popover': '10 100% 99% / 1',
    '--popover-foreground': '10 40% 15% / 1',
    '--primary': '10 100% 55% / 1',
    '--primary-foreground': '10 100% 98% / 1',
    '--secondary': '25 100% 80% / 1',
    '--secondary-foreground': '10 40% 15% / 1',
    '--muted': '10 50% 90% / 1',
    '--muted-foreground': '10 40% 35% / 1',
    '--accent': '0 100% 70% / 1',
    '--accent-foreground': '10 40% 15% / 1',
    '--destructive': '0 84% 60% / 1',
    '--destructive-foreground': '10 100% 98% / 1',
    '--border': '10 50% 85% / 1',
    '--input': '10 100% 99% / 1',
    '--ring': '10 100% 55% / 1'
  },
  'Vibrant': {
    '--background': '280 100% 95% / 1',
    '--foreground': '280 80% 20% / 1',
    '--card': '0 0% 100% / 1',
    '--card-foreground': '280 80% 20% / 1',
    '--popover': '0 0% 100% / 1',
    '--popover-foreground': '280 80% 20% / 1',
    '--primary': '280 100% 60% / 1',
    '--primary-foreground': '0 0% 100% / 1',
    '--secondary': '320 100% 70% / 1',
    '--secondary-foreground': '280 80% 20% / 1',
    '--muted': '280 60% 90% / 1',
    '--muted-foreground': '280 80% 20% / 1',
    '--accent': '300 100% 60% / 1',
    '--accent-foreground': '280 80% 20% / 1',
    '--destructive': '0 72% 51% / 1',
    '--destructive-foreground': '0 0% 100% / 1',
    '--border': '280 13% 91% / 1',
    '--input': '0 0% 100% / 1',
    '--ring': '280 100% 60% / 1'
  },
  'Midnight': {
    '--background': '240 10% 8% / 1',
    '--foreground': '240 10% 95% / 1',
    '--card': '240 10% 12% / 1',
    '--card-foreground': '240 10% 95% / 1',
    '--popover': '240 10% 12% / 1',
    '--popover-foreground': '240 10% 95% / 1',
    '--primary': '240 100% 60% / 1',
    '--primary-foreground': '240 10% 8% / 1',
    '--secondary': '240 10% 20% / 1',
    '--secondary-foreground': '240 10% 95% / 1',
    '--muted': '240 10% 20% / 1',
    '--muted-foreground': '240 10% 70% / 1',
    '--accent': '240 10% 20% / 1',
    '--accent-foreground': '240 10% 95% / 1',
    '--destructive': '0 84% 60% / 1',
    '--destructive-foreground': '240 10% 95% / 1',
    '--border': '240 10% 25% / 1',
    '--input': '240 10% 12% / 1',
    '--ring': '240 100% 60% / 1'
  },
  'Rose': {
    '--background': '350 100% 98% / 1',
    '--foreground': '350 40% 15% / 1',
    '--card': '350 100% 99% / 1',
    '--card-foreground': '350 40% 15% / 1',
    '--popover': '350 100% 99% / 1',
    '--popover-foreground': '350 40% 15% / 1',
    '--primary': '350 100% 55% / 1',
    '--primary-foreground': '350 100% 98% / 1',
    '--secondary': '340 100% 85% / 1',
    '--secondary-foreground': '350 40% 15% / 1',
    '--muted': '350 50% 92% / 1',
    '--muted-foreground': '350 40% 35% / 1',
    '--accent': '330 100% 70% / 1',
    '--accent-foreground': '350 40% 15% / 1',
    '--destructive': '0 84% 60% / 1',
    '--destructive-foreground': '350 100% 98% / 1',
    '--border': '350 50% 88% / 1',
    '--input': '350 100% 99% / 1',
    '--ring': '350 100% 55% / 1'
  },
  'Neutral': {
    '--background': '0 0% 98% / 1',
    '--foreground': '0 0% 15% / 1',
    '--card': '0 0% 100% / 1',
    '--card-foreground': '0 0% 15% / 1',
    '--popover': '0 0% 100% / 1',
    '--popover-foreground': '0 0% 15% / 1',
    '--primary': '0 0% 25% / 1',
    '--primary-foreground': '0 0% 98% / 1',
    '--secondary': '0 0% 85% / 1',
    '--secondary-foreground': '0 0% 15% / 1',
    '--muted': '0 0% 92% / 1',
    '--muted-foreground': '0 0% 45% / 1',
    '--accent': '0 0% 80% / 1',
    '--accent-foreground': '0 0% 15% / 1',
    '--destructive': '0 84% 60% / 1',
    '--destructive-foreground': '0 0% 98% / 1',
    '--border': '0 0% 88% / 1',
    '--input': '0 0% 100% / 1',
    '--ring': '0 0% 25% / 1'
  },
  'Warm': {
    '--background': '50 50% 98% / 1',
    '--foreground': '50 40% 15% / 1',
    '--card': '50 50% 100% / 1',
    '--card-foreground': '50 40% 15% / 1',
    '--popover': '50 50% 100% / 1',
    '--popover-foreground': '50 40% 15% / 1',
    '--primary': '50 100% 45% / 1',
    '--primary-foreground': '50 50% 98% / 1',
    '--secondary': '60 100% 80% / 1',
    '--secondary-foreground': '50 40% 15% / 1',
    '--muted': '50 30% 92% / 1',
    '--muted-foreground': '50 40% 35% / 1',
    '--accent': '40 100% 70% / 1',
    '--accent-foreground': '50 40% 15% / 1',
    '--destructive': '0 84% 60% / 1',
    '--destructive-foreground': '50 50% 98% / 1',
    '--border': '50 30% 88% / 1',
    '--input': '50 50% 100% / 1',
    '--ring': '50 100% 45% / 1'
  },
  'Cool': {
    '--background': '240 50% 98% / 1',
    '--foreground': '240 40% 15% / 1',
    '--card': '240 50% 100% / 1',
    '--card-foreground': '240 40% 15% / 1',
    '--popover': '240 50% 100% / 1',
    '--popover-foreground': '240 40% 15% / 1',
    '--primary': '240 100% 45% / 1',
    '--primary-foreground': '240 50% 98% / 1',
    '--secondary': '250 100% 80% / 1',
    '--secondary-foreground': '240 40% 15% / 1',
    '--muted': '240 30% 92% / 1',
    '--muted-foreground': '240 40% 35% / 1',
    '--accent': '260 100% 70% / 1',
    '--accent-foreground': '240 40% 15% / 1',
    '--destructive': '0 84% 60% / 1',
    '--destructive-foreground': '240 50% 98% / 1',
    '--border': '240 30% 88% / 1',
    '--input': '240 50% 100% / 1',
    '--ring': '240 100% 45% / 1'
  },
  'Elegant': {
    '--background': '320 30% 98% / 1',
    '--foreground': '320 40% 15% / 1',
    '--card': '320 30% 100% / 1',
    '--card-foreground': '320 40% 15% / 1',
    '--popover': '320 30% 100% / 1',
    '--popover-foreground': '320 40% 15% / 1',
    '--primary': '320 100% 45% / 1',
    '--primary-foreground': '320 30% 98% / 1',
    '--secondary': '340 100% 80% / 1',
    '--secondary-foreground': '320 40% 15% / 1',
    '--muted': '320 20% 92% / 1',
    '--muted-foreground': '320 40% 35% / 1',
    '--accent': '340 100% 70% / 1',
    '--accent-foreground': '320 40% 15% / 1',
    '--destructive': '0 84% 60% / 1',
    '--destructive-foreground': '320 30% 98% / 1',
    '--border': '320 20% 88% / 1',
    '--input': '320 30% 100% / 1',
    '--ring': '320 100% 45% / 1'
  },
  'Classic Red': {
    '--background': '0 0% 98% / 1',
    '--foreground': '0 0% 15% / 1',
    '--card': '0 0% 100% / 1',
    '--card-foreground': '0 0% 15% / 1',
    '--popover': '0 0% 100% / 1',
    '--popover-foreground': '0 0% 15% / 1',
    '--primary': '0 100% 50% / 1',
    '--primary-foreground': '0 0% 98% / 1',
    '--secondary': '0 0% 85% / 1',
    '--secondary-foreground': '0 0% 15% / 1',
    '--muted': '0 0% 92% / 1',
    '--muted-foreground': '0 0% 45% / 1',
    '--accent': '0 100% 70% / 1',
    '--accent-foreground': '0 0% 15% / 1',
    '--destructive': '0 84% 60% / 1',
    '--destructive-foreground': '0 0% 98% / 1',
    '--border': '0 0% 88% / 1',
    '--input': '0 0% 100% / 1',
    '--ring': '0 100% 50% / 1'
  },
  'Elegance Red': {
    '--background': '0 20% 98% / 1',
    '--foreground': '0 30% 15% / 1',
    '--card': '0 15% 99% / 1',
    '--card-foreground': '0 30% 15% / 1',
    '--popover': '0 15% 99% / 1',
    '--popover-foreground': '0 30% 15% / 1',
    '--primary': '0 85% 45% / 1',
    '--primary-foreground': '0 20% 98% / 1',
    '--secondary': '0 25% 88% / 1',
    '--secondary-foreground': '0 30% 15% / 1',
    '--muted': '0 20% 94% / 1',
    '--muted-foreground': '0 25% 40% / 1',
    '--accent': '0 75% 65% / 1',
    '--accent-foreground': '0 30% 15% / 1',
    '--destructive': '0 80% 55% / 1',
    '--destructive-foreground': '0 20% 98% / 1',
    '--border': '0 20% 90% / 1',
    '--input': '0 15% 99% / 1',
    '--ring': '0 85% 45% / 1'
  },
  'Aurora': {
    '--background': '160 50% 98% / 1',
    '--foreground': '160 40% 15% / 1',
    '--card': '160 50% 100% / 1',
    '--card-foreground': '160 40% 15% / 1',
    '--popover': '160 50% 100% / 1',
    '--popover-foreground': '160 40% 15% / 1',
    '--primary': '160 100% 45% / 1',
    '--primary-foreground': '160 50% 98% / 1',
    '--secondary': '180 100% 80% / 1',
    '--secondary-foreground': '160 40% 15% / 1',
    '--muted': '160 30% 92% / 1',
    '--muted-foreground': '160 40% 35% / 1',
    '--accent': '140 100% 70% / 1',
    '--accent-foreground': '160 40% 15% / 1',
    '--destructive': '0 84% 60% / 1',
    '--destructive-foreground': '160 50% 98% / 1',
    '--border': '160 30% 88% / 1',
    '--input': '160 50% 100% / 1',
    '--ring': '160 100% 45% / 1'
  },
  'Coral': {
    '--background': '15 50% 98% / 1',
    '--foreground': '15 40% 15% / 1',
    '--card': '15 50% 100% / 1',
    '--card-foreground': '15 40% 15% / 1',
    '--popover': '15 50% 100% / 1',
    '--popover-foreground': '15 40% 15% / 1',
    '--primary': '15 100% 45% / 1',
    '--primary-foreground': '15 50% 98% / 1',
    '--secondary': '25 100% 80% / 1',
    '--secondary-foreground': '15 40% 15% / 1',
    '--muted': '15 30% 92% / 1',
    '--muted-foreground': '15 40% 35% / 1',
    '--accent': '5 100% 70% / 1',
    '--accent-foreground': '15 40% 15% / 1',
    '--destructive': '0 84% 60% / 1',
    '--destructive-foreground': '15 50% 98% / 1',
    '--border': '15 30% 88% / 1',
    '--input': '15 50% 100% / 1',
    '--ring': '15 100% 45% / 1'
  },
  'Capuchin Blue': {
    '--background': '220 50% 98% / 1',
    '--foreground': '220 40% 15% / 1',
    '--card': '220 50% 99% / 1',
    '--card-foreground': '220 40% 15% / 1',
    '--popover': '220 50% 99% / 1',
    '--popover-foreground': '220 40% 15% / 1',
    '--primary': '220 100% 45% / 1',
    '--primary-foreground': '220 50% 98% / 1',
    '--secondary': '230 100% 80% / 1',
    '--secondary-foreground': '220 40% 15% / 1',
    '--muted': '220 30% 90% / 1',
    '--muted-foreground': '220 40% 35% / 1',
    '--accent': '240 100% 70% / 1',
    '--accent-foreground': '220 40% 15% / 1',
    '--destructive': '0 84% 60% / 1',
    '--destructive-foreground': '220 50% 98% / 1',
    '--border': '220 30% 85% / 1',
    '--input': '220 50% 99% / 1',
    '--ring': '220 100% 45% / 1'
  },
  'Capuchin Green': {
    '--background': '100 30% 98% / 1',
    '--foreground': '100 40% 15% / 1',
    '--card': '100 30% 99% / 1',
    '--card-foreground': '100 40% 15% / 1',
    '--popover': '100 30% 99% / 1',
    '--popover-foreground': '100 40% 15% / 1',
    '--primary': '100 100% 35% / 1',
    '--primary-foreground': '100 30% 98% / 1',
    '--secondary': '120 100% 80% / 1',
    '--secondary-foreground': '100 40% 15% / 1',
    '--muted': '100 20% 90% / 1',
    '--muted-foreground': '100 40% 35% / 1',
    '--accent': '80 100% 70% / 1',
    '--accent-foreground': '100 40% 15% / 1',
    '--destructive': '0 84% 60% / 1',
    '--destructive-foreground': '100 30% 98% / 1',
    '--border': '100 20% 85% / 1',
    '--input': '100 30% 99% / 1',
    '--ring': '100 100% 35% / 1'
  },
  'Capuchin Dark': {
    '--background': '25 30% 8% / 1',
    '--foreground': '45 100% 95% / 1',
    '--card': '25 30% 12% / 1',
    '--card-foreground': '45 100% 95% / 1',
    '--popover': '25 30% 12% / 1',
    '--popover-foreground': '45 100% 95% / 1',
    '--primary': '25 95% 53% / 1',
    '--primary-foreground': '25 30% 8% / 1',
    '--secondary': '35 100% 20% / 1',
    '--secondary-foreground': '45 100% 95% / 1',
    '--muted': '25 30% 20% / 1',
    '--muted-foreground': '45 50% 70% / 1',
    '--accent': '15 100% 40% / 1',
    '--accent-foreground': '45 100% 95% / 1',
    '--destructive': '0 84% 60% / 1',
    '--destructive-foreground': '45 100% 95% / 1',
    '--border': '25 30% 25% / 1',
    '--input': '25 30% 12% / 1',
    '--ring': '25 95% 53% / 1'
  },
  'Capuchin Blue Dark': {
    '--background': '210 40% 8% / 1',
    '--foreground': '210 50% 95% / 1',
    '--card': '210 40% 12% / 1',
    '--card-foreground': '210 50% 95% / 1',
    '--popover': '210 40% 12% / 1',
    '--popover-foreground': '210 50% 95% / 1',
    '--primary': '210 100% 45% / 1',
    '--primary-foreground': '210 40% 8% / 1',
    '--secondary': '200 100% 20% / 1',
    '--secondary-foreground': '210 50% 95% / 1',
    '--muted': '210 30% 20% / 1',
    '--muted-foreground': '210 50% 70% / 1',
    '--accent': '220 100% 40% / 1',
    '--accent-foreground': '210 50% 95% / 1',
    '--destructive': '0 84% 60% / 1',
    '--destructive-foreground': '210 50% 95% / 1',
    '--border': '210 30% 25% / 1',
    '--input': '210 40% 12% / 1',
    '--ring': '210 100% 45% / 1'
  },
  'Capuchin Green Dark': {
    '--background': '120 30% 8% / 1',
    '--foreground': '120 40% 95% / 1',
    '--card': '120 30% 12% / 1',
    '--card-foreground': '120 40% 95% / 1',
    '--popover': '120 30% 12% / 1',
    '--popover-foreground': '120 40% 95% / 1',
    '--primary': '120 100% 35% / 1',
    '--primary-foreground': '120 30% 8% / 1',
    '--secondary': '140 100% 20% / 1',
    '--secondary-foreground': '120 40% 95% / 1',
    '--muted': '120 20% 20% / 1',
    '--muted-foreground': '120 40% 70% / 1',
    '--accent': '100 100% 40% / 1',
    '--accent-foreground': '120 40% 95% / 1',
    '--destructive': '0 84% 60% / 1',
    '--destructive-foreground': '120 40% 95% / 1',
    '--border': '120 20% 25% / 1',
    '--input': '120 30% 12% / 1',
    '--ring': '120 100% 35% / 1'
  },
  'Capuchin Purple': {
    '--background': '270 30% 98% / 1',
    '--foreground': '270 40% 15% / 1',
    '--card': '270 30% 99% / 1',
    '--card-foreground': '270 40% 15% / 1',
    '--popover': '270 30% 99% / 1',
    '--popover-foreground': '270 40% 15% / 1',
    '--primary': '270 100% 35% / 1',
    '--primary-foreground': '270 30% 98% / 1',
    '--secondary': '280 100% 80% / 1',
    '--secondary-foreground': '270 40% 15% / 1',
    '--muted': '270 20% 90% / 1',
    '--muted-foreground': '270 40% 35% / 1',
    '--accent': '260 100% 70% / 1',
    '--accent-foreground': '270 40% 15% / 1',
    '--destructive': '0 84% 60% / 1',
    '--destructive-foreground': '270 30% 98% / 1',
    '--border': '270 20% 85% / 1',
    '--input': '270 30% 99% / 1',
    '--ring': '270 100% 35% / 1'
  },
  'Capuchin Purple Dark': {
    '--background': '270 40% 8% / 1',
    '--foreground': '270 30% 95% / 1',
    '--card': '270 40% 12% / 1',
    '--card-foreground': '270 30% 95% / 1',
    '--popover': '270 40% 12% / 1',
    '--popover-foreground': '270 30% 95% / 1',
    '--primary': '270 100% 35% / 1',
    '--primary-foreground': '270 40% 8% / 1',
    '--secondary': '280 100% 20% / 1',
    '--secondary-foreground': '270 30% 95% / 1',
    '--muted': '270 30% 15% / 1',
    '--muted-foreground': '270 30% 65% / 1',
    '--accent': '260 100% 40% / 1',
    '--accent-foreground': '270 30% 95% / 1',
    '--destructive': '0 84% 60% / 1',
    '--destructive-foreground': '270 40% 8% / 1',
    '--border': '270 30% 20% / 1',
    '--input': '270 40% 12% / 1',
    '--ring': '270 100% 35% / 1'
  }
};

// Categorize presets
const PRESET_CATEGORIES = {
  classic: ['Current', 'Original', 'Light', 'Dark', 'Neutral', 'Warm', 'Cool', 'Elegant', 'Classic Red', 'Elegance Red'],
  capuchin: ['Capuchin', 'Capuchin Dark', 'Capuchin Blue', 'Capuchin Blue Dark', 'Capuchin Green', 'Capuchin Green Dark', 'Capuchin Purple', 'Capuchin Purple Dark'],
  themed: ['Ocean', 'Forest', 'Sunset', 'Vibrant', 'Midnight', 'Rose', 'Aurora', 'Coral']
};

function createPaletteCard(name, palette) {
  const card = document.createElement('div');
  card.className = 'bg-white rounded-xl shadow-md hover:shadow-xl transition-all duration-300 border border-gray-200 overflow-hidden palette-card';
  card.setAttribute('data-palette-name', name);
  
  // Create color preview squares
  const colorSquares = Object.entries(palette).slice(0, 8).map(([key, value]) => {
    const hslMatch = value.match(/^(\d+)\s+(\d+)%\s+(\d+)%\s*\/\s*([\d.]+)$/);
    if (!hslMatch) return '';
    
    const [, h, s, l, a] = hslMatch;
    const hex = hslToHex(parseInt(h), parseInt(s), parseInt(l));
    
    // Determine border color based on lightness
    const lightness = parseInt(l);
    const borderColor = lightness > 70 ? '#d1d5db' : lightness > 40 ? '#9ca3af' : '#374151';
    
    return `<div class="w-8 h-8 rounded-lg color-square shadow-sm" style="background: linear-gradient(135deg, ${hex} 0%, ${hex} 100%); border: 2px solid ${borderColor};" title="${key}"></div>`;
  }).join('');
  
  card.innerHTML = `
    <div class="p-4">
      <div class="flex items-center justify-between mb-3">
        <h4 class="font-semibold text-gray-800 text-sm">${name}</h4>
        <button class="apply-palette-btn bg-gradient-to-r from-amber-500 to-yellow-500 hover:from-amber-600 hover:to-yellow-600 text-white px-3 py-1 rounded text-xs font-medium transition-all duration-300 shadow-sm flex items-center gap-1" data-palette="${name}">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-3 h-3">
            <path stroke-linecap="round" stroke-linejoin="round" d="M7.5 7.5h-.75A2.25 2.25 0 004.5 9.75v7.5a2.25 2.25 0 002.25 2.25h7.5a2.25 2.25 0 002.25-2.25v-7.5a2.25 2.25 0 00-2.25-2.25h-.75m-6 3l-3-3m0 0l-3 3m3-3v11.25m6-5.25h-.75a2.25 2.25 0 00-2.25 2.25v7.5a2.25 2.25 0 002.25 2.25h7.5a2.25 2.25 0 002.25-2.25v-7.5a2.25 2.25 0 00-2.25-2.25h-.75" />
          </svg>
          Apply
        </button>
      </div>
      <div class="grid grid-cols-4 gap-2 mb-3">
        ${colorSquares}
      </div>
      <div class="text-xs text-gray-500">
        ${Object.keys(palette).length} colors
      </div>
    </div>
  `;
  
  return card;
}

function populatePaletteTabs() {
  // Populate Classic tab
  const classicContainer = document.querySelector('#classic-palettes .grid');
  if (classicContainer) {
    classicContainer.innerHTML = '';
    PRESET_CATEGORIES.classic.forEach(name => {
      const palette = FIXED_PRESETS[name];
      if (palette) {
        classicContainer.appendChild(createPaletteCard(name, palette));
      }
    });
  }
  
  // Populate Capuchin tab
  const capuchinContainer = document.querySelector('#capuchin-palettes .grid');
  if (capuchinContainer) {
    capuchinContainer.innerHTML = '';
    PRESET_CATEGORIES.capuchin.forEach(name => {
      const palette = FIXED_PRESETS[name];
      if (palette) {
        capuchinContainer.appendChild(createPaletteCard(name, palette));
      }
    });
  }
  
  // Populate Themed tab
  const themedContainer = document.querySelector('#themed-palettes .grid');
  if (themedContainer) {
    themedContainer.innerHTML = '';
    PRESET_CATEGORIES.themed.forEach(name => {
      const palette = FIXED_PRESETS[name];
      if (palette) {
        themedContainer.appendChild(createPaletteCard(name, palette));
      }
    });
  }
}

function getCustomPresets() {
  try {
    const stored = localStorage.getItem('brand_custom_presets');
    return stored ? JSON.parse(stored) : {};
  } catch {
    return {};
  }
}

function getPresetPalette(name) {
  if (name.startsWith('__custom__')) {
    const custom = getCustomPresets();
    return custom[name.replace('__custom__', '')];
  }
  return FIXED_PRESETS[name] || null;
}

function previewPreset(name) {
  const palette = getPresetPalette(name);
  if (!palette) return;
  
  // Update COLOR_VARIABLES in-place for preview only
  COLOR_VARIABLES.forEach(cv => {
    if (palette[cv.name]) {
      cv.value = palette[cv.name];
    }
  });
  renderColorPaletteTable();
}

// Form handling
function handleBrandForm(formId, fieldName) {
  const form = document.getElementById(formId);
  if (!form) return;
  
  form.addEventListener('submit', async function(e) {
    e.preventDefault();
    const formData = new FormData();
    const fileInput = form.querySelector('input[type="file"]');
    if (!fileInput.files.length) {
      showToast('warning', 'Pilih file terlebih dahulu!');
      return;
    }
    formData.append(fieldName, fileInput.files[0]);
    try {
      const headers = {};
      const csrfToken = getCSRFToken();
      if (csrfToken) {
        headers['X-CSRFToken'] = csrfToken;
      }
      
      const resp = await fetch('/api/brand-identity', {
        method: 'POST',
        headers: headers,
        body: formData
      });
      if (!resp.ok) throw new Error('Upload failed');
      showToast('success', 'Gambar berhasil diunggah!');
      refreshBrandImages();
      form.reset();
    } catch (err) {
      console.error('Upload error:', err);
      showToast('error', 'Gagal mengunggah gambar: ' + err.message);
    }
  });
}

function handleBrandTextForm(formId, fieldName) {
  const form = document.getElementById(formId);
  if (!form) return;
  
  form.addEventListener('submit', async function(e) {
    e.preventDefault();
    const input = form.querySelector('input[type="text"], textarea');
    const value = input.value.trim();
    
    if (!value) {
      showToast('warning', 'Field tidak boleh kosong!');
      return;
    }
    
    try {
      const headers = {
        'Content-Type': 'application/json',
      };
      const csrfToken = getCSRFToken();
      if (csrfToken) {
        headers['X-CSRFToken'] = csrfToken;
      }
      
      const resp = await fetch('/api/brand-identity/text', {
        method: 'POST',
        headers: headers,
        body: JSON.stringify({
          field: fieldName,
          value: value
        })
      });
      
      if (!resp.ok) throw new Error('Update failed');
      
      const labels = { brand_name: 'Brand name', tagline: 'Tagline', brand_description: 'Brand description' };
      showToast('success', `${labels[fieldName] || fieldName} berhasil diperbarui!`);
      
      // Update the input value to reflect the saved state
      input.value = value;
      
    } catch (err) {
      console.error('Update error:', err);
      const errLabels = { brand_name: 'brand name', tagline: 'tagline', brand_description: 'brand description' };
      showToast('error', `Gagal memperbarui ${errLabels[fieldName] || fieldName}: ` + err.message);
    }
  });
}

// fetchWithCSRF wrapper — adds CSRF header automatically
async function fetchWithCSRF(url, options = {}) {
  const csrfToken = getCSRFToken();
  if (csrfToken) {
    options.headers = options.headers || {};
    options.headers['X-CSRFToken'] = csrfToken;
  }
  return fetch(url, options);
}

// Asset type name helper
function getAssetTypeName(fieldName) {
  const names = {
    'logo_header': 'Logo Header',
    'logo_footer': 'Logo Footer',
    'favicon': 'Favicon',
    'placeholder_image': 'Placeholder'
  };
  return names[fieldName] || 'Gambar';
}

// Homepage Design Management
function handleHomepageDesignForm(formId) {
  const form = document.getElementById(formId);
  if (!form) return;
  const newForm = form.cloneNode(true);
  form.parentNode.replaceChild(newForm, form);
  newForm.addEventListener('submit', async function(e) {
    e.preventDefault();
    const btn = newForm.querySelector('button[type="submit"]');
    const originalText = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<svg class="animate-spin -ml-1 mr-3 h-4 w-4 text-white" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/></svg> Updating...';
    const designType = new FormData(newForm).get('homepage_design');
    try {
      const resp = await fetchWithCSRF('/api/brand-identity/text', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ field: 'homepage_design', value: designType })
      });
      if (!resp.ok) throw new Error(await resp.json().then(d => d.error).catch(() => `HTTP ${resp.status}`));
      showToast('success', 'Homepage design updated!');
      document.querySelectorAll('[name="homepage_design"]').forEach(el => {
        const btn = el.closest('form').querySelector('button[type="submit"]');
        if (btn) btn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-4 h-4"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg> ' + (btn.closest('form').id === formId ? 'Active' : 'Set as Active');
      });
    } catch (err) {
      showToast('error', 'Failed: ' + err.message);
    } finally {
      btn.disabled = false;
      btn.innerHTML = originalText;
    }
  });
}

// Categories Display Location Management
function handleCategoriesDisplayForm(formId) {
  const form = document.getElementById(formId);
  if (!form) return;
  const newForm = form.cloneNode(true);
  form.parentNode.replaceChild(newForm, form);
  newForm.addEventListener('submit', async function(e) {
    e.preventDefault();
    const btn = newForm.querySelector('button[type="submit"]');
    const originalText = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<svg class="animate-spin -ml-1 mr-3 h-4 w-4 text-white" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/></svg> Updating...';
    const location = new FormData(newForm).get('categories_display_location');
    try {
      const resp = await fetchWithCSRF('/api/brand-identity/text', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ field: 'categories_display_location', value: location })
      });
      if (!resp.ok) throw new Error(await resp.json().then(d => d.error).catch(() => `HTTP ${resp.status}`));
      showToast('success', 'Categories display updated!');
      document.querySelectorAll('[name="categories_display_location"]').forEach(el => {
        const btn = el.closest('form').querySelector('button[type="submit"]');
        if (btn) btn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-4 h-4"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg> ' + (btn.closest('form').id === formId ? 'Active' : 'Set as Active');
      });
    } catch (err) {
      showToast('error', 'Failed: ' + err.message);
    } finally {
      btn.disabled = false;
      btn.innerHTML = originalText;
    }
  });
}

// Card Design Management
function handleCardDesignForm(formId) {
  const form = document.getElementById(formId);
  if (!form) return;
  const newForm = form.cloneNode(true);
  form.parentNode.replaceChild(newForm, form);
  newForm.addEventListener('submit', async function(e) {
    e.preventDefault();
    const btn = newForm.querySelector('button[type="submit"]');
    const originalText = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<svg class="animate-spin -ml-1 mr-3 h-4 w-4 text-white" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/></svg> Updating...';
    const cardDesign = new FormData(newForm).get('card_design');
    try {
      const resp = await fetchWithCSRF('/api/brand-identity/text', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ field: 'card_design', value: cardDesign })
      });
      if (!resp.ok) throw new Error(await resp.json().then(d => d.error).catch(() => `HTTP ${resp.status}`));
      showToast('success', 'Card design updated!');
      document.querySelectorAll('[name="card_design"]').forEach(el => {
        const btn = el.closest('form').querySelector('button[type="submit"]');
        if (btn) btn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-4 h-4"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg> ' + (btn.closest('form').id === formId ? 'Active' : 'Set as Active');
      });
      window.dispatchEvent(new CustomEvent('cardDesignChanged', { detail: { cardDesign } }));
    } catch (err) {
      showToast('error', 'Failed: ' + err.message);
    } finally {
      btn.disabled = false;
      btn.innerHTML = originalText;
    }
  });
}

// Feature toggle handler — for enable_* boolean fields
function handleFeatureToggle(toggleId, fieldName) {
  const toggle = document.getElementById(toggleId);
  if (!toggle) return;
  toggle.addEventListener('change', async function() {
    try {
      const resp = await fetchWithCSRF('/api/brand-identity/text', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ field: fieldName, value: this.checked })
      });
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      showToast('success', `${fieldName} diperbarui!`);
    } catch (err) {
      this.checked = !this.checked;
      showToast('error', 'Gagal: ' + err.message);
    }
  });
}

// Invalidate CSS cache
function invalidateBrandCache() {
  const link = document.querySelector('link[href*="base_css.css"]');
  if (link) link.href = link.href.split('?')[0] + '?v=' + Date.now();
}

// Initialize everything
document.addEventListener('DOMContentLoaded', function() {
  // Load color palette
  fetch('/api/brand-colors')
    .then(resp => resp.json())
    .then(data => {
      COLOR_VARIABLES = data;
      populatePaletteTabs();
      renderColorPaletteTable();
    })
    .catch(err => console.error('Failed to load colors:', err));
  
  // Brand form handlers
  handleBrandForm('form-logo-header', 'logo_header');
  handleBrandForm('form-logo-footer', 'logo_footer');
  handleBrandForm('form-favicon', 'favicon');
  handleBrandForm('form-placeholder', 'placeholder_image');
  
  // Brand text form handlers
  handleBrandTextForm('form-brand-name', 'brand_name');
  handleBrandTextForm('form-tagline', 'tagline');
  handleBrandTextForm('form-brand-description', 'brand_description');
  
  // Design system form handlers
  handleHomepageDesignForm('form-homepage-news');
  handleHomepageDesignForm('form-homepage-editorial');
  handleHomepageDesignForm('form-homepage-professional');
  
  // Categories display form handlers
  handleCategoriesDisplayForm('form-categories-body');
  handleCategoriesDisplayForm('form-categories-navbar');
  handleCategoriesDisplayForm('form-categories-none');
  
  // Card design form handlers
  handleCardDesignForm('form-card-classic');
  handleCardDesignForm('form-card-modern');
  handleCardDesignForm('form-card-minimal');
  handleCardDesignForm('form-card-featured');
  
  // Feature toggle handlers
  document.querySelectorAll('[data-feature-toggle]').forEach(el => {
    handleFeatureToggle(el.id, el.getAttribute('data-feature-toggle'));
  });
  
  // Tab switching functionality
  const paletteTabs = document.querySelectorAll('.palette-tab');
  paletteTabs.forEach(tab => {
    tab.addEventListener('click', function() {
      const targetTab = this.getAttribute('data-tab');
      
      // Update tab states
      paletteTabs.forEach(t => {
        // Remove all possible gradient classes
        t.classList.remove('active', 'bg-gradient-to-r', 'from-amber-500', 'to-yellow-500', 'from-blue-500', 'to-indigo-500', 'from-gray-400', 'to-gray-500');
        // Add gray gradient for inactive
        t.classList.add('bg-gradient-to-r', 'from-gray-400', 'to-gray-500');
        t.setAttribute('aria-selected', 'false');
      });
      
      // Add amber gradient for active tab
      this.classList.add('active', 'bg-gradient-to-r', 'from-amber-500', 'to-yellow-500');
      this.classList.remove('bg-gradient-to-r', 'from-gray-400', 'to-gray-500', 'from-blue-500', 'to-indigo-500');
      this.setAttribute('aria-selected', 'true');
      
      // Show/hide content
      const allContents = document.querySelectorAll('.palette-content');
      allContents.forEach(content => content.classList.add('hidden'));
      
      const targetContent = document.getElementById(`${targetTab}-palettes`);
      if (targetContent) {
        targetContent.classList.remove('hidden');
      }
    });
  });
  
  // Apply palette functionality
  document.addEventListener('click', async function(e) {
    if (e.target.classList.contains('apply-palette-btn')) {
      const paletteName = e.target.getAttribute('data-palette');
      const palette = getPresetPalette(paletteName);
      
      if (!palette) {
        showToast('warning', 'Palette tidak ditemukan!');
        return;
      }
      
      console.log('Applying palette:', paletteName);
      console.log('Palette data:', palette);
      
      // Create array of updates needed
      const updates = [];
      
      COLOR_VARIABLES.forEach(cv => {
        const presetValue = palette[cv.name];
        if (presetValue) {
          // Normalize values for comparison
          const currentNormalized = cv.value.trim().replace(/\s+/g, ' ').replace(/\s*\/\s*/, ' / ');
          const presetNormalized = presetValue.trim().replace(/\s+/g, ' ').replace(/\s*\/\s*/, ' / ');
          
          if (currentNormalized !== presetNormalized) {
            updates.push({
              variable: cv.name,
              value: presetValue
            });
          }
        }
      });
      
      if (updates.length === 0) {
        showToast('info', 'Tidak ada warna yang perlu diperbarui!');
        return;
      }
      
      console.log('Applying palette with', updates.length, 'updates');
      
      try {
        // Apply all updates
        for (const update of updates) {
          const headers = {
            'Content-Type': 'application/json'
          };
          const csrfToken = getCSRFToken();
          if (csrfToken) {
            headers['X-CSRFToken'] = csrfToken;
          }
          
          const response = await fetch('/api/brand-colors', {
            method: 'POST',
            headers: headers,
            body: JSON.stringify(update)
          });
          
          if (!response.ok) {
            throw new Error(`Failed to update ${update.variable}`);
          }
        }
        
        // Reload palette from backend
        const response = await fetch('/api/brand-colors');
        const data = await response.json();
        COLOR_VARIABLES = data;
        renderColorPaletteTable();
        
        // Reload CSS
        const link = document.querySelector('link[href*="base_css.css"]');
        if (link) {
          link.href = link.href.split('?')[0] + '?v=' + Date.now();
        }
        
        showToast('success', `Palette "${paletteName}" berhasil diterapkan!`);
      } catch (err) {
        console.error('Error applying palette:', err);
        showToast('error', 'Gagal menerapkan palette: ' + err.message);
      }
    }
  });
  

  
  // Add keyboard event listener for modal
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
      const modal = document.getElementById('color-picker-modal');
      if (modal && !modal.classList.contains('hidden')) {
        closeColorPickerModal();
      }
    }
  });
});
