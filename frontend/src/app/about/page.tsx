"use client";
import React, { useState, useEffect } from 'react';;
import MaxWidthWrapper from '../../components/MaxWidthWrapper';


const AboutPage: React.FC = () => {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-white dark:bg-black">
      <MaxWidthWrapper>
        <section className="flex flex-col items-center justify-center py-12 space-y-8">
          This is about page and it is under development
        </section>
      </MaxWidthWrapper>
    </div>
  );
};
export default AboutPage;
