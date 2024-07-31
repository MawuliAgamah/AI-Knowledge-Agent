BroadUserPrompt = """
Career Goal: Become a lead data scientist within one year in the UK civil service

The data i have made available to you is as follows :
- My Current CV
- Job descriptions for positions i would like to apply to.

Request: Develop a comprehensive one-year career advancement plan that addresses the following areas:

1. Skills and Qualifications:
   - Identify specific technical and soft skills required for a lead data scientist role
   - Determine any gaps between current skillset and desired qualifications

2. Learning and Development:
   - Recommend relevant courses, certifications, and training programs
   - Prioritize learning objectives based on impact and time investment

3. Career Progression Timeline:
   - Outline key milestones and set realistic deadlines
   - Suggest methods for tracking and evaluating progress

4. Performance Enhancement:
   - Provide strategies for improving current job performance
   - Recommend ways to gain relevant leadership and project management experience

5. Application Optimization:
   - Offer tips for tailoring CV and job applications to Grade 7 data scientist positions
   - Suggest effective ways to highlight newly acquired skills and experiences

6. Additional Recommendations:
   - Propose networking strategies and industry engagement opportunities
   - Advise on building a professional online presence (e.g., LinkedIn, GitHub)
   - Suggest relevant conferences, workshops, or seminars to attend

Please provide detailed, actionable advice for each area, considering the provided resources and the one-year timeframe. Include specific examples and practical steps where possible.
"""


#task_planner_promp = f'Take the following prompt : {query2}.  Break this down prompt down into a tasks
#                              Which can then be fed into a langiage model prompts which can then be actioned'

Planner_prompt = f"""
        Analyze the following career development prompt:

        {BroadUserPrompt}

        Please provide a structured breakdown of this prompt into smaller sub-tasks.

        For each sub-task, create a detailed sub-prompt that can be used as input by another language model to query a database to get relevant information. 

        The output should be a JSON list of objects, each containing the following fields:
        - "task_number": The identifier for a task, for example "Task 1"
        - "task_description": A sub-prompt that includes specific instructions for the language model to query the database for relevant information. Include the data at hand, such as CV and job descriptions, when generating sub-prompts.

        Ensure each sub-prompt is clear, specific, and actionable.
"""


example_json = {
   "tasks": [
      {
         "task_number": "Task 1",
         "task_description": "Identify specific technical and soft skills required for a lead data scientist role.",
         "sub_prompt": "Given the current CV and the job descriptions for positions the user would like to apply to, list the specific technical and soft skills required for a lead data scientist role in the UK civil service."
      },
      {
         "task_number": "Task 2",
         "task_description": "Determine any gaps between the current skillset and the desired qualifications for a lead data scientist role.",
         "sub_prompt": "Compare the skills listed in the current CV with the skills required in the job descriptions. Identify and list any gaps in technical and soft skills that need to be addressed."
      },
      {
         "task_number": "Task 3",
         "task_description": "Recommend relevant courses, certifications, and training programs to bridge the skill gaps identified.",
         "sub_prompt": "Based on the identified skill gaps, suggest relevant courses, certifications, and training programs that can help the user acquire the necessary skills. Provide options with varying time investments and impacts."
      },
      {
         "task_number": "Task 4",
         "task_description": "Prioritize learning objectives based on impact and time investment.",
         "sub_prompt": "Given the recommended courses and training programs, prioritize the learning objectives. Consider the impact on the user's career goals and the time investment required for each course or program."
      },
      {
         "task_number": "Task 5",
         "task_description": "Outline key milestones and set realistic deadlines for achieving the career goal.",
         "sub_prompt": "Develop a timeline with key milestones for achieving the career goal of becoming a lead data scientist within one year. Include realistic deadlines for each milestone based on the learning objectives and skill acquisition plan."
      },
      {
         "task_number": "Task 6",
         "task_description": "Provide strategies for improving current job performance.",
         "sub_prompt": "Suggest specific strategies and actions the user can take to enhance their current job performance. Include ways to demonstrate leadership and project management skills relevant to a lead data scientist role."
      },
      {
         "task_number": "Task 7",
         "task_description": "Recommend ways to gain relevant leadership and project management experience.",
         "sub_prompt": "Identify opportunities within the user's current role or external projects where they can gain leadership and project management experience. Provide examples of relevant experiences that would be valuable for a lead data scientist position."
      },
      {
         "task_number": "Task 8",
         "task_description": "Offer tips for tailoring the CV and job applications to Grade 7 data scientist positions.",
         "sub_prompt": "Provide specific tips and examples for tailoring the user's CV and job applications to align with Grade 7 data scientist positions in the UK civil service. Highlight how to effectively showcase newly acquired skills and experiences."
      },
      {
         "task_number": "Task 9",
         "task_description": "Suggest effective ways to highlight newly acquired skills and experiences in the CV and job applications.",
         "sub_prompt": "Recommend strategies for presenting new skills and experiences in the CV and job applications. Provide examples of impactful phrasing and formatting to ensure these additions stand out to recruiters."
      },
      {
         "task_number": "Task 10",
         "task_description": "Propose networking strategies and industry engagement opportunities.",
         "sub_prompt": "List effective networking strategies and opportunities for industry engagement that can help the user connect with professionals in the field. Include suggestions for both online and offline networking."
      },
      {
         "task_number": "Task 11",
         "task_description": "Advise on building a professional online presence (e.g., LinkedIn, GitHub).",
         "sub_prompt": "Provide detailed advice on how to build and enhance a professional online presence. Include tips for optimizing LinkedIn profiles, creating a GitHub portfolio, and engaging with relevant online communities."
      },
      {
         "task_number": "Task 12",
         "task_description": "Suggest relevant conferences, workshops, or seminars to attend.",
         "sub_prompt": "Identify relevant conferences, workshops, and seminars that the user should attend to further their knowledge and network with industry professionals. Provide details on how to make the most of these events."
      }
   ]
}

example_quert_json = {
  "query": "Tips for tailoring CV and job applications to Grade 7 data scientist positions and effective ways to highlight newly acquired skills and experiences considering a one-year career advancement plan and provided resources"
}
