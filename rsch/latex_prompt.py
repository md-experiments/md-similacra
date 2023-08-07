from langchain.prompts.prompt import PromptTemplate

_DEFAULT_ENTITY_EXTRACTION_TEMPLATE = """You are an AI assistant analysing a piece of text written in LaTeX. 
Extract the relevant text content that is going to appear when converted into pdf. 
Return the text verbatim, do not embellish or change the content.
Only return the exact text from the Input snippet and nothing more. Do not start with "Sure" or add any clarification text.
If for some reason you cannot retrieve the text or perform the task just respond with: NONE


EXAMPLE
\section{Introduction}
\renewcommand{\thefootnote}{}% Empty \thefootnote
\footnote{* Equal contribution. Correspondence to \url{ktian@college.harvard.edu}, \url{eric.mitchell@cs.stanford.edu}.}%
\renewcommand{\thefootnote}{\arabic{footnote}}% Standard \thefootnote
A trustworthy prediction system should produce not just predictions, but \textit{well-calibrated} probabilities: the model's confidence in a prediction should accurately reflect the probability that the prediction is correct \citep{guo2017calibration}. In the context of language models, one consequence of poor calibration may be \textit{hallucination}, where a language model confidently asserts incorrect facts or reasoning. While the ability of very large LMs to absorb, synthesize, and recombine knowledge about the outside world has gained significant attention \citep{brown2020language,roberts2020much,bubeck2023sparks}, relatively little attention has been given to their well-calibratedness \citep{kadavath2022language}. Further, most existing analyses of the calibratedness of LLMs focuses on models trained with maximum likelihood, while in practice, the most widely-used LLMs (such as ChatGPT) are fine-tuned from a pre-trained generative model with methods such as reinforcement learning from human feedback \citep{christiano2017deep}. Some findings have suggested that RLHF-LMs may sacrifice well-calibrated predictions for the sake of closer adherence to user instructions in dialogue \citep{kadavath2022language,openai2023gpt4}, as the reinforcement learning objective encourages the model to allocate as much probability mass as possible to the most likely answer, rather than matching the relative frequency of possible answers.

\begin{figure*}
    \centering
    \includegraphics[width=\textwidth]{figures/fig1_sciq_v2_fit.png}
    %%XCF:  Can you make the x-axis and y-axis labels larger? They are tiny and really hard to read.
    \caption{Calibration plots and ECE for \texttt{gpt-3.5-turbo} on the SciQ science question-answering dataset. For each bar corresponding to a range of x-axis values, the height of the bar is the average accuracy of model predictions whose confidence falls within the x-axis range. Darker bars mean a larger percentage of model predictions fall into that range. Using raw model probabilities \textbf{(left; Label Prob.)} to assess confidence leads to consistent over-confidence. Using directly verbalized numerical probabilities \textbf{(middle three plots; Verb. 1S top-$k$)} provides significantly improved calibration, with calibration improving as the model produces more possible hypotheses before giving a confidence score (mirroring the phenomenon of `Considering the Opposite' in human psychology; \citet{lord1985considering}). Alternatively to verbalized numerical probabilities, verbalizing linguistic \textit{expressions of likelihood} \textbf{(right)} also provides well-calibrated confidences.}
    \vspace{-4mm}
    \label{fig:calibration-plots}
\end{figure*}

In this paper, we evaluate a collection of methods for extracting confidences about model predictions from RLHF-LMs. Due to concerns that RLHF may cause systematic overconfidence in the model's probabilities, as well as the general unavailability of per-token log-probabilities in widely used RLHF-LMs, we pay particular attention to prompting strategies that elicit \textit{verbalized} probabilities, i.e., the model expresses its confidence in token-space, as either numerical probabilities or another linguistic expression of uncertainty. 
%%XCF: I think the preface to this sentence is a bit misleading. This isn't the only reason that we consider verbalized probabilities.
We find that, surprisingly, popular RLHF-LMs are able to verbalize confidence scores directly that are better-calibrated than the true conditional probabilities of the model (estimated via sampling), even without \emph{any} fine-tuning specifically for verbalizing confidence accurately. 
%%XCF: Is there a way to convey that this result is perhaps surprising?
Inspired by research in human psychology showing that overconfidence can be mitigated by considering alternative answers before responding \citep{lord1985considering,mussweiler2000overcoming}, we show that prompting a model to produce several answer choices before giving its confidence scores significantly improves calibration of verbalized probabilities. Combined with temperature scaling \citep{guo2017calibration}, this approach consistently improves the calibration of ChatGPT and GPT-4 across datasets, reducing expected calibration error (ECE) by well over 50\% on average.


\noindent\textbf{Related Work.} Several studies have examined the calibration of large LMs \citep{lin2022teaching,park-caragea-2022-calibration,kadavath2022language,xiao-etal-2022-uncertainty,kuhn2023semantic}, finding that combining large pre-trained LMs with temperature scaling \citep{guo2017calibration} produces very well-calibrated predictions \citep{kadavath2022language,xiao-etal-2022-uncertainty,kuhn2023semantic}. Other works focus on the tendency of language and dialogue models to use linguistic expressions of uncertainty in a well-calibrated manner \citep{zhou2023navigating,mielke-etal-2022-reducing}. However, existing studies focus on LMs trained purely with supervised learning (\citet{kadavath2022language} briefly examine RLHF-LMs), while widely-used models in practice are fine-tuned with instruction-tuning or RLHF \citep{christiano2017deep}. RLHF has been shown to effectively leverage annotations of human preferences to control sentiment \citep{ziegler2020finetuning}, improve summarization or instruction-following quality \citep{stiennon2022learning,ouyang2022training}, and inject behavioral priors of harmlessness \citep{bai2022constitutional,bai2022training}. However, recent work has raised the question of whether or not RLHF is damaging to calibration \citep{openai2023gpt4}.
%%XCF: The above sentence is a mouthful. Do you really need the part after "the latter of which..."? That latter part doesn't seem that related to calibration, so it doesn't seem essential.
Our work is the first to perform a targeted analysis of the calibration of RLHF-LMs, focusing on ChatGPT and GPT-4.

END OF EXAMPLE

EXAMPLE

Reference statements:
{history}
Statements for extraction:
{input}

Output:"""

ENTITY_EXTRACTION_PROMPT = PromptTemplate(
    input_variables=["history", "input"], template=_DEFAULT_ENTITY_EXTRACTION_TEMPLATE
)