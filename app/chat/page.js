"use client"
import styles from './chat.css'
import FormSection from '../components/FormSection';
import AnswerSection from '../components/AnswerSection';

import { useState } from 'react';

function getData(prompt) {
  return fetch("https://joe91.pythonanywhere.com/call?group=pma&prompt=" + prompt + "&memory=no")
      .then((res) => res.json())
      .then(function(data) {
        console.log(prompt)
        return data;
      })
}

export default function Home() {
  const [storedValues, setStoredValues] = useState([]);

  const generateResponse = async (newQuestion, setNewQuestion) => {

    if (newQuestion) {

      let response = await getData(newQuestion)

      if (response.text) {
        setStoredValues([
          {
            question: newQuestion,
            answer: response.text,
          },
          ...storedValues,
        ]);
        setNewQuestion('');
      }
    }
  }

  return (
      <div>
        <div className="header-section">
          <h1>OpenDoor</h1>
          <p>
            Welcome to AI powered property management solutions
          </p>
        </div>

        <FormSection generateResponse={generateResponse} />
        <AnswerSection storedValues={storedValues} />
      </div>
  );
};
